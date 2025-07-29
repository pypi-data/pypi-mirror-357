from typer.testing import CliRunner
from chatops.cli import app
from chatops import env as env_mod, config
import chatops.providers.docker as docker_provider

runner = CliRunner()

def test_logs_tail(monkeypatch, tmp_path):
    home = tmp_path
    cfg_dir = home / ".chatops"
    cfg_dir.mkdir()
    cfg_file = cfg_dir / "config.yaml"
    cfg_file.write_text("environments:\n  docker-local:\n    provider: docker\n")
    monkeypatch.setattr(env_mod, "ACTIVE_FILE", cfg_dir / ".active_env")
    monkeypatch.setattr(env_mod, "SANDBOX_DIR", cfg_dir / "sandboxes")
    monkeypatch.setattr(config, "CONFIG_FILE", cfg_file)
    monkeypatch.setattr(docker_provider, "prompt_and_authenticate", lambda env: None)
    monkeypatch.setattr(docker_provider, "tail_logs", lambda e, svc, n: [f"{svc} line {i}" for i in range(n)])
    runner.invoke(app, ["env", "use", "docker-local"], env={"HOME": str(home)})
    result = runner.invoke(app, ["logs", "myservice"], env={"HOME": str(home)})
    assert result.exit_code == 0
    assert "myservice line" in result.output
