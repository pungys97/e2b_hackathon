import glob
import os
import json
import argparse
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import openai
from dotenv import load_dotenv
from e2b import Sandbox
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("react_gpt_engineer")

load_dotenv()

# Default templates path
TEMPLATES_DIR = (
    Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "templates"
)


class ReactGPTEngineer:
    """
    ReactGPTEngineer generates simple React applications based on detailed prompts
    and tests them in an E2B sandbox environment.
    """

    # Predefined folder structure for React apps
    FOLDER_STRUCTURE = {
        "src": {
            "components": {},
        },
        "public": {},
    }

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        output_dir: str = "./react-app",
        templates_dir: Optional[str] = None,
        max_iterations: int = 1,
    ):
        """
        Initialize the React GPT Engineer.

        Args:
            openai_api_key: OpenAI API key (defaults to os.environ["OPENAI_API_KEY"])
            model: OpenAI model to use
            temperature: Temperature for generation (higher = more creative)
            output_dir: Directory to store generated code
            templates_dir: Directory containing prompt templates
            max_iterations: Maximum number of iterations to attempt fixing issues
        """
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError(
                "OpenAI API key must be provided or set as OPENAI_API_KEY environment variable"
            )

        self.client = openai.OpenAI(api_key=self.openai_api_key)
        self.model = model
        self.temperature = temperature
        self.output_dir = Path(output_dir)
        self.templates_dir = Path(templates_dir) if templates_dir else TEMPLATES_DIR
        self.max_iterations = max_iterations
        self.conversation_history = []

    def create_folder_structure(self):
        """Create the predefined folder structure for the React app"""
        logger.info(f"Creating folder structure in {self.output_dir}...")

        def create_nested_dirs(base_path, structure):
            for dir_name, sub_dirs in structure.items():
                dir_path = base_path / dir_name
                dir_path.mkdir(exist_ok=True, parents=True)

                if isinstance(sub_dirs, dict) and sub_dirs:
                    create_nested_dirs(dir_path, sub_dirs)

        self.output_dir.mkdir(exist_ok=True, parents=True)
        create_nested_dirs(self.output_dir, self.FOLDER_STRUCTURE)

        # Create basic package.json, README.md and .gitignore
        with open(self.output_dir / "package.json", "w") as f:
            json.dump(
                {
                    "name": self.output_dir.name,
                    "version": "0.1.0",
                    "private": True,
                    "dependencies": {
                        "react": "^18.2.0",
                        "react-dom": "^18.2.0",
                        "react-scripts": "5.0.1",
                        "typescript": "^4.9.5",
                    },
                    "scripts": {
                        "start": "react-scripts start",
                        "build": "react-scripts build",
                    },
                    "eslintConfig": {"extends": ["react-app", "react-app/jest"]},
                    "browserslist": {
                        "production": [">0.2%", "not dead", "not op_mini all"],
                        "development": [
                            "last 1 chrome version",
                            "last 1 firefox version",
                            "last 1 safari version",
                        ],
                    },
                },
                f,
                indent=2,
            )

        with open(self.output_dir / "README.md", "w") as f:
            f.write(
                f"# {self.output_dir.name}\n\nA simple React application generated by ReactGPTEngineer.\n"
            )

        with open(self.output_dir / ".gitignore", "w") as f:
            f.write("node_modules\n.env\nbuild\n.DS_Store\n")

    def load_template(self, template_name: str) -> str:
        """
        Load a prompt template from file.

        Args:
            template_name: Name of the template file

        Returns:
            Content of the template file
        """
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            logger.warning(
                f"Template file {template_path} not found. Using default template."
            )
            return ""

        with open(template_path, "r") as f:
            return f.read()

    def generate_app(self, prompt: str) -> Dict[str, str]:
        """
        Generate a simple React application based on the prompt.

        Args:
            prompt: Detailed description of the React app to build

        Returns:
            Dictionary mapping file paths to code content
        """
        logger.info("Generating React components based on the prompt...")

        # Load system prompt from template file
        system_message = self.load_template("system_prompt.txt")

        assert system_message.strip() != "", "System prompt template is empty"

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ]

        # Store conversation history for iterations
        self.conversation_history = messages.copy()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                response_format={"type": "json_object"},
                messages=messages,
            )

            response_content = response.choices[0].message.content
            self.conversation_history.append(
                {"role": "assistant", "content": response_content}
            )

            response_json = json.loads(response_content)

            # Convert to dictionary mapping paths to content
            files_dict = {}
            for file_info in response_json.get("files", []):
                files_dict[file_info["path"]] = file_info["content"]

            return files_dict

        except Exception as e:
            logger.error(f"Error generating React app: {e}")
            raise

    def save_app(self, components: Dict[str, str]) -> str:
        """
        Save the generated React app to the output directory.

        Args:
            components: Dictionary mapping file paths to code content

        Returns:
            Path to the output directory
        """
        logger.info(f"Saving generated React app to {self.output_dir}...")

        # Create folder structure first
        self.create_folder_structure()

        # Save all generated files
        for file_path, content in components.items():
            full_path = self.output_dir / file_path
            full_path.parent.mkdir(exist_ok=True, parents=True)

            with open(full_path, "w") as f:
                f.write(content)

        return str(self.output_dir)

    def test_in_sandbox(self, timeout: int = 600) -> Sandbox | None:
        """
        Test the generated React app in an E2B sandbox.

        Args:
            timeout: Maximum time (seconds) to wait for tests to complete

        Returns:
            Sandbox if build is successful, else None.
        """
        logger.info("Setting up E2B sandbox for testing...")

        # Create a new sandbox instance
        template_id = "jr829l6nnqz8gwyfpzbh"
        sandbox = Sandbox(template_id, timeout=timeout)

        # Upload all generated files
        file_paths = glob.glob(f"{self.output_dir}/**/*.*", recursive=True)

        logger.info("Uploading generated files to sandbox...")
        for file_path in file_paths:
            with open(file_path, "r") as f:
                sandbox.files.write(file_path, open(file_path, "r"))

        # Run npm install
        logger.info("Installing dependencies in sandbox...")
        install_process = sandbox.commands.run(
            "cd react-app && npm install", timeout=timeout
        )

        if install_process.exit_code != 0:
            return None

        # Run npm build
        logger.info("Building the React app...")
        build_process = sandbox.command.run(
            "cd react-app && npm run build", timeout=timeout
        )

        if build_process.exit_code != 0:
            return None

        return sandbox

    def iterate_with_feedback(
        self, test_results: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """
        Improve the application based on feedback and/or test results.

        Args:
            test_results: Results from testing the application (optional)

        Returns:
            Dictionary mapping file paths to updated content
        """
        logger.info("Iterating on the application with feedback...")

        # Load the feedback template
        feedback_message = self.load_template("iteration_prompt.txt")

        assert feedback_message.strip() != "", "Feedback template is empty"

        # Prepare context about current state
        file_listing = "\n".join(
            f"- {path}"
            for path in os.listdir(self.output_dir)
            if Path(self.output_dir / path).is_file()
        )

        # Create feedback prompt
        feedback_message += f"""
        Current build issues:
        
        CURRENT FILES:
        {file_listing}
        
        TEST RESULTS:
        {json.dumps(test_results) if test_results else "No test results available."}
        """

        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": feedback_message})

        # Get AI response
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                response_format={"type": "json_object"},
                messages=self.conversation_history,
            )

            response_content = response.choices[0].message.content
            self.conversation_history.append(
                {"role": "assistant", "content": response_content}
            )

            response_json = json.loads(response_content)

            # Extract updated files
            files_dict = {}
            for file_info in response_json.get("files", []):
                files_dict[file_info["path"]] = file_info["content"]

            return files_dict

        except Exception as e:
            logger.error(f"Error during iteration: {e}")
            raise

    def run(self, prompt: str, max_iterations: int = 2) -> Dict[str, Any]:
        """
        Generate a React app based on prompt and test it in the sandbox.

        Args:
            prompt: Detailed description of the React app to build
            max_iterations: Maximum number of iterations to attempt fixing issues

        Returns:
            Dictionary containing app files and test results
        """
        # Use iterative development
        logger.info("Starting iterative development process...")

        result = {"success": False}

        # Generate initial app
        # app_files = self.generate_app(prompt)
        # self.save_app(app_files)
        iterations = 1

        while iterations <= max_iterations:
            sandbox = self.test_in_sandbox()
            if sandbox:
                break
            app_files = self.iterate_with_feedback(result)
            self.save_app(app_files)
            iterations += 1

        if sandbox:
            logger.info("✅ React app built successfully!")

            # Serve the react app
            sandbox.commands.run("cd react-app && npm start --port 3000", timeout=300)
            url = "https://" + sandbox.get_host(3000)
            logger.infor(f"Serving app: {url}")
        else:
            logger.warning(
                "❌ React app build failed. Check the test results for details."
            )

        return result


def main():
    parser = argparse.ArgumentParser(description="React GPT Engineer")
    parser.add_argument(
        "--prompt", type=str, help="Detailed prompt describing the React app to build"
    )
    parser.add_argument(
        "--prompt-file", type=str, help="Path to file containing the detailed prompt"
    )

    args = parser.parse_args()

    # Get prompt from either command line or file
    if args.prompt:
        prompt = args.prompt
    elif args.prompt_file:
        with open(args.prompt_file, "r") as f:
            prompt = f.read()
    else:
        parser.error("Either --prompt or --prompt-file must be provided")

    # Initialize and run React GPT Engineer
    engineer = ReactGPTEngineer()

    result = engineer.run(prompt=prompt)

    if result["success"]:
        logger.info("✅ Final result: React app built successfully!")
    else:
        logger.warning("❌ Final result: React app build failed.")


if __name__ == "__main__":
    main()
