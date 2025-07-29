from typer.testing import CliRunner
from pathlib import Path
from chatops.cli import app
from chatops import env as env_mod, config

runner = CliRunner()


def test_env_use_and_current(tmp_path, monkeypatch):
    home = tmp_path
    (home / ".chatops").mkdir()
    cfg = home / ".chatops" / "config.yaml"
    cfg.write_text(
        "environments:\n  aws-test:\n    provider: aws\n"
    )
    monkeypatch.setattr(env_mod, "ACTIVE_FILE", home / ".chatops" / ".active_env")
    monkeypatch.setattr(config, "CONFIG_FILE", cfg)
    import chatops.providers.aws as aws_provider
    monkeypatch.setattr(aws_provider, "prompt_and_authenticate", lambda env: None)
    runner.invoke(app, ["env", "use", "aws-test"], env={"HOME": str(home)})
    result = runner.invoke(app, ["env", "current"], env={"HOME": str(home)})
    assert "aws-test" in result.output


def test_env_list(tmp_path, monkeypatch):
    home = tmp_path
    cfg = home / ".chatops"
    cfg.mkdir()
    cfg_file = cfg / "config.yaml"
    cfg_file.write_text(
        "environments:\n  local:\n    provider: local\n  docker:\n    provider: docker\n"
    )
    monkeypatch.setattr(env_mod, "ACTIVE_FILE", cfg / ".active_env")
    monkeypatch.setattr(config, "CONFIG_FILE", cfg_file)
    result = runner.invoke(app, ["env", "list"], env={"HOME": str(home)})
    assert "local" in result.output
    assert "docker" in result.output


def test_gcp_provider_validation(tmp_path, monkeypatch):
    home = tmp_path
    cfg = home / ".chatops"
    cfg.mkdir()
    cfg_file = cfg / "config.yaml"
    cfg_file.write_text(
        "environments:\n  gcp-test:\n    provider: gcp\n"
    )
    monkeypatch.setattr(config, "CONFIG_FILE", cfg_file)
    # Should not raise
    config.validate_env("gcp-test")


def test_env_use_creates_sandbox(tmp_path, monkeypatch):
    home = tmp_path
    cfg = home / ".chatops"
    cfg.mkdir()
    cfg_file = cfg / "config.yaml"
    cfg_file.write_text(
        "environments:\n  gcp-test:\n    provider: gcp\n"
    )
    monkeypatch.setattr(env_mod, "ACTIVE_FILE", cfg / ".active_env")
    monkeypatch.setattr(env_mod, "SANDBOX_DIR", cfg / "sandboxes")
    import chatops.providers.gcp as gcp_provider
    monkeypatch.setattr(gcp_provider, "prompt_and_authenticate", lambda env: None)
    monkeypatch.setattr(config, "CONFIG_FILE", cfg_file)
    runner.invoke(app, ["env", "use", "gcp-test"], env={"HOME": str(home)})
    sandbox = cfg / "sandboxes" / "gcp-test"
    assert sandbox.exists()
    assert (sandbox / "provider").read_text() == "gcp"



def test_env_status(tmp_path, monkeypatch):
    home = tmp_path
    cfg = home / ".chatops"
    cfg.mkdir()
    cfg_file = cfg / "config.yaml"
    cfg_file.write_text(
        "environments:\n  aws-prod:\n    provider: aws\n"
    )
    monkeypatch.setattr(env_mod, "ACTIVE_FILE", cfg / ".active_env")
    monkeypatch.setattr(config, "CONFIG_FILE", cfg_file)
    (cfg / ".active_env").write_text("aws-prod")
    import chatops.providers.aws as aws_provider
    monkeypatch.setattr(aws_provider, "is_authenticated", lambda env: True)
    result = runner.invoke(app, ["env", "status"], env={"HOME": str(home)})
    assert "authenticated" in result.output
