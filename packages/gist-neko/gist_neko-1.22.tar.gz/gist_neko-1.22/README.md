# gist-neko

CLI for downloading all gists from a specified user.

## Requirements

`requests` is used to get information from the Github API and download the gists (if you don't use -g/--git to download using git).

Note that `requests` will not download submodules but git will.

If you want to build this on your own, you can install the requirements with

```Python
pip install -r requirements.txt
```

or install the package by running

```Python
pip install gist-neko
```

Python's native `os` (used to check for whether a folder exists or not), `argparse` (parse return request and set command argument), `subprocess` (call `git clone` and `git pull` on gists) and `setuptools` (used to build the script) packages are also used.

## How it works

I send requests to `https://api.github.com/users/{username}/gists`, depending on the arguments passed to the script, I either download all the gists in specified user's account with either `requests` or `git`.

You can run the script with

```Python
gist-neko
    -u <github-username>
    -t <github-personal-access-token> (optional - you will just download the public gists instead of all gists)
    -e (optional - means you will be using environment variables. This overrides -u and -t)
    -g (optional - means you will be downloading using git)
    -gu <github-username> (this will set <github-username> as environment variable)
    -gpat <github-personal-access-token> (this will set <github-personal-access-token> as environment variable)
```

### Examples

#### Setting Environment Variables

This will set the specified **Github username** and **personal access token** as your `GITHUB_USERNAME` and `GITHUB_PERSONAL_ACCESS_TOKEN` environment variable respectively. On Linux this is a bit buggy.

```Python
gist-neko -gu <github-username> -gpat <github-personal-access-token>
```

This will set the specified **Github username** as your `GITHUB_USERNAME` environment variable. On Linux this is a bit buggy.

```Python
gist-neko -gu <github-username>
```

This will set the specified **personal access token** as your `GITHUB_PERSONAL_ACCESS_TOKEN` environment variable. On Linux this is a bit buggy.

```Python
gist-neko -gpat <github-personal-access-token>
```

#### Public Gists without Environment Variables

This will use the specified **Github username** and download all **public gists** using `requests`.

```Python
gist-neko -u <github-username> -t <github-personal-access-token>
```

This will use the specified **Github username** and download all **public gists** using `git`.

```Python
gist-neko -u <github-username> -t <github-personal-access-token> -g <anything>
```

#### Public and Private Gists without Environment Variables

This will use the specified **Github username** and **personal access token** and download all **public and private gists** using `requests`.

```Python
gist-neko -u <github-username> -t <github-personal-access-token>
```

This will use the specified **Github username** and **personal access token** and download all **public and private gists** using `git`.

```Python
gist-neko -u <github-username> -t <github-personal-access-token> -g <anything>
```

#### Public and Private Gists with Environment Variables

This will use the **Github username** and **personal access token** in the **environment variables** and download all **public and private gists** using `requests`.

```Python
gist-neko -e <anything>
```

This will use the **Github username** and **personal access token** in the **environment variables** and download all **public and private gists** using `git`.

```Python
gist-neko -e <anything> -g <anything>
```

#### Public and Private Gists with Environment Variables (Overriding passed Username and Personal Access Token)

This will **ignore** the passed **Github username** and **personal access token** instead using **environment variables** and download all **public and private gists** using `requests`.

```Python
gist-neko -u <github-username> -t <github-personal-access-token> -e <anything>
```

This will **ignore** the passed **Github username** and **personal access token** instead using **environment variables** and download all **public and private gists** using `git`.

```Python
gist-neko -u <github-username> -t <github-personal-access-token> -e <anything> -g <anything>
```

### Simplified Examples

If you want to only download your gists (public), you can do

```Python
gist-neko -u <your-username>
```

If you want to only download your gists (public and private), you can either do

```Python
gist-neko -u <your-username> -t <your-personal-access-token>
```

or you can put your information on environment variables and do

```Python
gist-neko -e <anything>
```

If you want to download other people's gists (public), you can do

```Python
gist-neko -u <their-username>
```

If you want to download other people's gists (public and private), you can do

```Python
gist-neko -u <their-username> -t <their-personal-access-token>
```
