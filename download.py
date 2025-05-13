from pathlib import Path
import ffmpeg


def download_file(url, filepath: Path):
    filepath.parent.mkdir(exist_ok=True, parents=True)

    stream = ffmpeg.input(url)
    output_stream = ffmpeg.output(
        stream, filepath.as_posix(), **{"c": "copy", "bsf:a": "aac_adtstoasc"}
    )

    print(output_stream.get_args())

    # ffmpeg.run(output_stream)
    ffmpeg.run_async(output_stream, quiet=False)
