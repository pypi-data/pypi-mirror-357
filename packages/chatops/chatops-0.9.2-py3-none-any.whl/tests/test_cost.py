from typer.testing import CliRunner
from chatops.cli import app
from chatops import env as env_mod, config

import chatops.providers.aws as aws_provider

runner = CliRunner()

def test_cost_report(monkeypatch, tmp_path):
    home = tmp_path
    cfg_dir = home / ".chatops"
    cfg_dir.mkdir()
    cfg_file = cfg_dir / "config.yaml"
    cfg_file.write_text("environments:\n  aws-prod:\n    provider: aws\n")
    monkeypatch.setattr(env_mod, "ACTIVE_FILE", cfg_dir / ".active_env")
    monkeypatch.setattr(env_mod, "SANDBOX_DIR", cfg_dir / "sandboxes")
    monkeypatch.setattr(config, "CONFIG_FILE", cfg_file)
    monkeypatch.setattr(aws_provider, "prompt_and_authenticate", lambda env: None)
    monkeypatch.setattr(aws_provider, "cost_report", lambda env: [("svc", 1.0)])
    runner.invoke(app, ["env", "use", "aws-prod"], env={"HOME": str(home)})
    result = runner.invoke(app, ["cost", "report"], env={"HOME": str(home)})
    assert result.exit_code == 0
    assert "svc" in result.output
