""" Database configuration loaded from enviroment variables."""


from dataclasses import dataclass
import os
from pathlib import Path


from dotenv import load_dotenv

"""Find the actual location of the file """
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


load_dotenv(ENV_FILE)


@dataclass(frozen=True)
class DatabaseConfig:
	"""PostgreSQL connection configuration."""


	host: str
	port: int
	name: str
	user: str
	password: str

	@classmethod
	def from_environment(cls) -> "DatabaseConfig":
		"""Create configuration using enviroment variables."""


		required_variables = {
			"DB_HOST": os.getenv("DB_HOST"),
			"DB_PORT": os.getenv("DB_PORT"),
			"DB_NAME": os.getenv("DB_NAME"),
			"DB_USER": os.getenv("DB_USER"),
			"DB_PASSWORD": os.getenv("DB_PASSWORD"),
		}


		missing_variables = [
			variable
			for variable, value in required_variables.items()
			if value is None or value.strip() == ""
		]


		if missing_variables:
			missing = ", ".join(missing_variables)

			raise ValueError(
				f"Missing required environment variables: {missing}"
			)

		port_value = required_variables["DB_PORT"]


		try:
			port = int(port_value)
		except ValueError as error:
			raise ValueError(
				"DB_PORT must be a valid integer."
			) from error

		return cls(
			host=required_variables["DB_HOST"],
			port=port,
			name=required_variables["DB_NAME"],
			user=required_variables["DB_USER"],
			password=required_variables["DB_PASSWORD"],
		)

database_config = DatabaseConfig.from_environment()
