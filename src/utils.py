# Borrowed from https://github.com/elevenlabs/elevenlabs-mcp

import os
from pathlib import Path
from datetime import datetime
from rapidfuzz import fuzz
import soundfile as sf
import sounddevice as sd
from mcp.types import TextContent

class MCPError(Exception):
    pass

def play_audio(file_path: str) -> TextContent:
    """
    Play an audio file using sounddevice and soundfile.
    
    Args:
        file_path: Path to the audio file to play
        
    Returns:
        TextContent with success message
    """
    # Validate and get the file path
    path = handle_input_file(file_path, audio_content_check=True)
    
    try:
        # Read the audio file
        data, samplerate = sf.read(path)
        
        # Play the audio (this will block until playback is finished)
        sd.play(data, samplerate)
        sd.wait()  # Wait until playback is finished
        
        return TextContent(
            type="text",
            text=f"Successfully played audio file: {path}"
        )
    except Exception as e:
        make_error(f"Error playing audio file: {str(e)}")


def make_error(error_text: str):
    raise MCPError(error_text)


def is_file_writeable(path: Path) -> bool:
    if path.exists():
        return os.access(path, os.W_OK)
    parent_dir = path.parent
    return os.access(parent_dir, os.W_OK)


def make_output_file(
    tool: str, text: str, output_path: Path, extension: str, full_id: bool = False
) -> Path:
    id = text if full_id else text[:5]

    output_file_name = f"{tool}_{id.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
    return output_path / output_file_name


def make_output_path(
    output_directory: str | None, base_path: str | None = None
) -> Path:
    # Get the base output path from environment variables or use the provided base_path
    base_output_path = os.environ.get("BASE_OUTPUT_PATH", base_path)

    # If base_output_path is still None, fall back to Desktop
    if base_output_path is None:
        base_output_path = str(Path.home() / "Desktop")

    # Expand user paths (like ~)
    base_output_path = os.path.expanduser(base_output_path)

    # If output_directory is None, use the base output path directly
    if output_directory is None:
        output_path = Path(base_output_path)
    # If output_directory is a relative path, join it with the base output path
    elif not os.path.isabs(output_directory):
        output_path = Path(base_output_path) / Path(output_directory)
    # If output_directory is an absolute path, use it directly
    else:
        output_path = Path(os.path.expanduser(output_directory))

    # Make sure the path is writeable
    if not is_file_writeable(output_path):
        make_error(f"Directory ({output_path}) is not writeable")

    # Create the directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    return output_path


def find_similar_filenames(
    target_file: str, directory: Path, threshold: int = 70
) -> list[tuple[str, int]]:
    """
    Find files with names similar to the target file using fuzzy matching.

    Args:
        target_file (str): The reference filename to compare against
        directory (str): Directory to search in (defaults to current directory)
        threshold (int): Similarity threshold (0 to 100, where 100 is identical)

    Returns:
        list: List of similar filenames with their similarity scores
    """
    target_filename = os.path.basename(target_file)
    similar_files = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if (
                filename == target_filename
                and os.path.join(root, filename) == target_file
            ):
                continue
            similarity = fuzz.token_sort_ratio(target_filename, filename)

            if similarity >= threshold:
                file_path = Path(root) / filename
                similar_files.append((file_path, similarity))

    similar_files.sort(key=lambda x: x[1], reverse=True)

    return similar_files


def try_find_similar_files(
    filename: str, directory: Path, take_n: int = 5, check_image: bool = False
) -> list[Path]:
    similar_files = find_similar_filenames(filename, directory)
    if not similar_files:
        return []

    filtered_files = []

    for path, _ in similar_files[:take_n]:
        if check_image and check_image_file(path):
            filtered_files.append(path)
        elif not check_image and check_audio_file(path):
            filtered_files.append(path)

    return filtered_files


def check_audio_file(path: Path) -> bool:
    audio_extensions = {
        ".wav",
        ".mp3",
        ".m4a",
        ".aac",
        ".ogg",
        ".flac",
        ".mp4",
        ".avi",
        ".mov",
        ".wmv",
    }
    return path.suffix.lower() in audio_extensions


def check_image_file(path: Path) -> bool:
    image_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".webp",
    }
    return path.suffix.lower() in image_extensions


def handle_input_file(file_path: str, audio_content_check: bool = False, image_content_check: bool = False) -> Path:
    if not os.path.isabs(file_path) and not os.environ.get("BASE_OUTPUT_PATH"):
        make_error(
            "File path must be an absolute path if BASE_OUTPUT_PATH is not set"
        )
    path = Path(file_path)
    if not path.exists() and path.parent.exists():
        parent_directory = path.parent
        similar_files = try_find_similar_files(path.name, parent_directory)
        similapir_files_formatted = ",".join([str(file) for file in similar_files])
        if similar_files:
            make_error(
                f"File ({path}) does not exist. Did you mean any of these files: {similar_files_formatted}?"
            )
        make_error(f"File ({path}) does not exist")
    elif not path.exists():
        make_error(f"File ({path}) does not exist")
    elif not path.is_file():
        make_error(f"File ({path}) is not a file")

    if audio_content_check and not check_audio_file(path):
        make_error(f"File ({path}) is not an audio or video file")
    if image_content_check and not check_image_file(path):
        make_error(f"File ({path}) is not an image file")
    return path


