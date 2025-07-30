import logging
from datetime import datetime

import FreeSimpleGUI as fsg
import obsws_python as obsws
from clypi import ClypiConfig, ClypiException, Command, Positional, arg, configure
from typing_extensions import override

logger = logging.getLogger(__name__)

config = ClypiConfig(
    nice_errors=(ClypiException,),
)
configure(config)


class Start(Command):
    """Start recording."""

    filename: Positional[str] = arg(
        default="default_name",
        help="Name of the recording",
        prompt="Enter the name for the recording",
    )
    host: str = arg(inherited=True)
    port: int = arg(inherited=True)
    password: str = arg(inherited=True)

    @staticmethod
    def get_timestamp():
        return datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    @override
    async def run(self):
        if not self.filename:
            raise ClypiException("Recording name cannot be empty.")

        with obsws.ReqClient(
            host=self.host, port=self.port, password=self.password
        ) as client:
            resp = client.get_record_status()
            if resp.output_active:
                raise ClypiException("Recording is already active.")

            client.set_profile_parameter(
                "Output",
                "FilenameFormatting",
                f"{self.filename} {self.get_timestamp()}",
            )
            client.start_record()


class Stop(Command):
    """Stop recording."""

    host: str = arg(inherited=True)
    port: int = arg(inherited=True)
    password: str = arg(inherited=True)

    @override
    async def run(self):
        with obsws.ReqClient(
            host=self.host, port=self.port, password=self.password
        ) as client:
            resp = client.get_record_status()
            if not resp.output_active:
                raise ClypiException("Recording is not active.")

            client.stop_record()


def theme_parser(value: str) -> str:
    """Parse the theme argument."""
    themes = ["Light Purple", "Neutral Blue", "Reds", "Sandy Beach"]
    if value not in themes:
        raise ClypiException(
            f"Invalid theme: {value}. Available themes: {', '.join(themes)}"
        )
    return value


class SimpleRecorder(Command):
    subcommand: Start | Stop | None = None
    host: str = arg(default="localhost", env="OBS_HOST")
    port: int = arg(default=4455, env="OBS_PORT")
    password: str | None = arg(default=None, env="OBS_PASSWORD")
    theme: str = arg(default="Reds", parser=theme_parser, env="OBS_THEME")

    @override
    async def run(self):
        fsg.theme(self.theme)

        input_text = fsg.InputText("", key="-FILENAME-")
        start_record_button = fsg.Button("Start Recording", key="Start Recording")
        stop_record_button = fsg.Button("Stop Recording", key="Stop Recording")

        layout = [
            [fsg.Text("Enter recording filename:")],
            [input_text],
            [start_record_button, stop_record_button],
            [fsg.Text("Status: Not started", key="-OUTPUT-")],
        ]
        window = fsg.Window("Simple Recorder", layout, finalize=True)
        status_text = window["-OUTPUT-"]
        input_text.bind("<Return>", "-ENTER-")
        start_record_button.bind("<Return>", "-ENTER-")
        stop_record_button.bind("<Return>", "-ENTER-")

        while True:
            event, values = window.read()
            logger.debug(f"Event: {event}, Values: {values}")
            if event == fsg.WIN_CLOSED:
                break
            elif event in (
                "Start Recording",
                "Start Recording-ENTER-",
                "-FILENAME--ENTER-",
            ):
                try:
                    await Start(
                        filename=input_text.get(),
                        host=self.host,
                        port=self.port,
                        password=self.password,
                    ).run()
                    status_text.update("Status: Recording started", text_color="green")
                except ClypiException as e:
                    status_text.update(str(e), text_color="red")
                    logger.error(f"Error starting recording: {e}")
            elif event in ("Stop Recording", "Stop Recording-ENTER-"):
                try:
                    await Stop(
                        host=self.host,
                        port=self.port,
                        password=self.password,
                    ).run()
                    status_text.update("Status: Recording stopped", text_color="green")
                except ClypiException as e:
                    status_text.update(str(e), text_color="red")
                    logger.error(f"Error stopping recording: {e}")


def run():
    """Run the CLI application."""
    SimpleRecorder.parse().start()


if __name__ == "__main__":
    run()
