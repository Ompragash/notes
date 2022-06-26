# How To Validate A PyPI Package Using Its PGP Signature?
This article explains validating a package's PGP signature downloaded from PyPI.

### Requirements
- `curl`
- `wget`

### Issue

In some instances, verifying the package downloaded from PyPi using its PGP signature is necessary. This is to ensure that the source code has not been modified/tampered with since it was packaged.

### Resolution

- Download the PGP signature file of a PyPi package by appending `.asc` to it's download URL. 

We can use PyPi's Simple API to get a package's download URL and then append `.asc`:

```bash
curl -s https://pypi.org/simple/ansible/ | grep -i ansible-6.0.0.tar.gz
```

You'll get the output like below:

~~~
curl -s https://pypi.org/simple/ansible/ | grep -i ansible-6.0.0.tar.gz
    <a href="https://files.pythonhosted.org/packages/45/10/dd811cf3525904d2e0d72d1f2ff237e884b36653951939ff42e2a31e04dd/ansible-6.0.0.tar.gz#sha256=641a2c27bc5768f9a8ad14880f1f6e571c1f2af1d45e76f271d76e3f74754c53" data-requires-python="&gt;=3.8" >ansible-6.0.0.tar.gz</a><br />
~~~

`href` section in the above output contains the download URL along with the _SHA256_ value.

- Now, download the tar file along with the PGP signature file (.asc) using `wget`

```bash
wget https://files.pythonhosted.org/packages/45/10/dd811cf3525904d2e0d72d1f2ff237e884b36653951939ff42e2a31e04dd/ansible-6.0.0.tar.gz
wget https://files.pythonhosted.org/packages/45/10/dd811cf3525904d2e0d72d1f2ff237e884b36653951939ff42e2a31e04dd/ansible-6.0.0.tar.gz.asc
```

- Verify the PGP Signature of the package

NOTE: Before verifying the PGP signature, make sure to download the public key of the software author and add it to your GPG public keyring.

Syntax to verify PGP signature:
```bash
gpg --verify PGP_SIGNATURE_FILE.asc DATA_FILE.tar.gz
```


```bash
gpg --verify ansible-6.0.0.tar.gz.asc ansible-6.0.0.tar.gz
```
