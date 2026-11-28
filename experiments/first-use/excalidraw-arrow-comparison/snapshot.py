"""Build the installed macOS source template from a local upstream Git repository."""
import argparse
from pathlib import Path
import subprocess
from lab import BASE, git


def prepare(repo, dest):
    dest.mkdir(parents=True, exist_ok=False)
    with subprocess.Popen(['git','-C',repo,'archive',BASE],stdout=subprocess.PIPE) as archive:
        subprocess.run(['tar','-xf','-','-C',dest],stdin=archive.stdout,check=True)
        archive.stdout.close()
        if archive.wait():
            raise RuntimeError('git archive failed')
    git(dest,'init','-q')
    subprocess.run(['npx','--yes','--package=yarn@1.22.22','-c',
                    'yarn install --frozen-lockfile --non-interactive'],cwd=dest,check=True)
    names = git(repo,'ls-tree','-rz','--name-only',BASE)
    git(dest,'add','-f','--pathspec-from-file=-','--pathspec-file-nul',data=names)
    assert git(dest,'write-tree') == git(repo,'rev-parse',BASE+'^{tree}')
    git(dest,'-c','user.name=Fixture','-c','user.email=fixture@example.invalid',
        'commit','-qm','Source snapshot')
    assert git(dest,'status','--porcelain') == b''


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository',type=Path)
    parser.add_argument('destination',type=Path)
    args=parser.parse_args()
    prepare(args.repository.resolve(),args.destination.resolve())
