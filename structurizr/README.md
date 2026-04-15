# How to use structurizr

See: https://docs.structurizr.com/local/quickstart

VS Code Expansion for DSL syntax highlighting: **ciarant.vscode-structurizr**

## Step by step

create your own directory or use the `structurizr` directory in the repo.
The folder should contain the `.dsl` files.

Start Docker Daemon / Docker Desktop

Pull the current image

```text
docker pull structurizr/structurizr
```

Run the container providing the correct PATH

```text
export STRUCTURIZR_PATH=~/structurizr

docker run -it --rm -p 8080:8080 \
  -v $STRUCTURIZR_PATH:/usr/local/structurizr \
  structurizr/structurizr local
```

Open `localhost:8080` in your broswer to open the application


