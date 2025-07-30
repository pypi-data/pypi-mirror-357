from pathlib import Path
import shutil

CAT_FOLDER = ".cat"

class Cat:

  def __init__(self, env_path: str) -> None:
    """
    env_path should be an absolute path
    """
    self.env_path = env_path
    self._initialize_cat_folder()
    
  def _initialize_cat_folder(self) -> None:
    """Initialize the .exp folder structure with required files and folders"""

    if not (Path(self.env_path) / ".git").exists():
      print("Cat only works in a git repository. Please initialize git first! thx")
      return

    cat_path = Path(self.env_path) / CAT_FOLDER
    if not cat_path.exists():
      print("Creating .cat folder 🐱")

      cat_path.mkdir()

      # Create empty JSON files
      (cat_path / "commit.json").write_text("{}")
      (cat_path / "branch.json").write_text("{}")
      
      # Create empty YAML config
      (cat_path / "config.yaml").write_text("")

      # Create required folders
      (cat_path / "agents").mkdir(exist_ok=True)
      (cat_path / "cache").mkdir(exist_ok=True)

      # Copy agents folder from source
      src_agents_path = Path(__file__).parent / "agents"
      shutil.copytree(src_agents_path, cat_path / "agents", dirs_exist_ok=True)
      
      # Copy models.py from source
      src_models_path = Path(__file__).parent / "models.py"
      shutil.copy2(src_models_path, cat_path / "models.py")

    else:
      print("Cat already exists 🐈 Remove .cat folder to reinitialize.")

  # TODO
  def _update_metadata(self) -> None:
    """Update commit and branch metadata"""
    pass

  # TODO
  def run(self) -> None:
    pass