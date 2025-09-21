# ./
# ├- git-over-fs/
# │  └- demo/ (namespace)
# │     ├- target/
# │     └- target.git/ (bare remote repository)
# │        └- hooks/
# │           └- post-receive
# └- source/ (non-bare local repository)

# Create a namespace, similar to users or organizations on GitHub
mkdir git-over-fs
mkdir $_/demo
# Initialize a bare repository
git init --bare $_/target.git
# Enable the post-receive hook for automatic deployment
mkdir ${_/.git} && cat << EOF > $_.git/hooks/post-receive
#!/bin/sh
git --work-tree="$(realpath $_)" checkout --force
EOF
# Make the post-receive hook executable
chmod +x $_.git/hooks/post-receive

# Create the source repository
git clone file://$PWD/demo/target.git source && cd $_
# Configure the user information if needed
git config --local user.email '<>' && git config --local user.name Felix
# Commit the first change
touch README.md && git add . && git commit -m 'Initial commit'
# Push onto the bare repository
git push
