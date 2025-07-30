from ...core import Context


def deploy_setup(c: Context):
    c.run("[ -d {{deploy_path}} ] || mkdir -p {{deploy_path}}")
    c.cd("{{deploy_path}}")
    c.run("[ -d .dep ] || mkdir .dep")
    c.run("[ -d releases ] || mkdir releases")
    c.run("[ -d shared ] || mkdir shared")

    if c.test("[ ! -L {{current_path}} ] && [ -d {{current_path}} ]"):
        c.raise_error(
            "There is a directory (not symlink) at {{current_path}}.\n Remove it, then it can be replaced with a symlink for atomic deployments."
        )

    c.info("The deploy path is ready ({{deploy_path}})")
