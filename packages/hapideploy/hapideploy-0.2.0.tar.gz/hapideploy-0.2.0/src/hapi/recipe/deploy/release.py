import json

from ...core import Context


def deploy_release(c: Context):
    c.cd("{{deploy_path}}")

    if c.test("[ -h release ]"):
        c.run("rm release")

    releases = c.cook("releases_list")
    release_name = c.cook("release_name")
    release_sub_dir = f"releases/{release_name}"

    if c.test(f"[ -d {release_sub_dir} ]"):
        c.raise_error(
            f'Release name "{release_name}" already exists.\nIt can be overridden via:\n --put=release_name=*'
        )

    c.run("echo {{release_name}} > .dep/latest_release")

    import time

    timestamp = time.time()
    import getpass

    user = getpass.getuser()

    candidate = {
        "created_at": timestamp,
        "release_name": str(release_name),
        "user": user,
        "target": c.cook("target"),
    }

    json_data = json.dumps(candidate)

    c.run(f"echo '{json_data}' >> .dep/releases_log")

    c.run(f"mkdir -p {release_sub_dir}")

    c.run("{{bin/symlink}} " + release_sub_dir + " {{deploy_path}}/release")

    c.info("The release path is symlinked ({{deploy_path}}/release)")

    releases.insert(0, release_name)

    if len(releases) >= 2:
        c.put("previous_release", "{{deploy_path}}/releases/" + releases[1])
