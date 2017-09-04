## Certificates

This folder will contain your bot certificates. At the moment, you must provide the certs as two .pem files. The names
of the files are specified in config.json:

`botinfo": {
    "botEmail": "bot.user@company.com",
    "certificatePath": "./certificates",
    "certificateFilePath": "bot.crt.pem",
    "certificateKeyfilePath": "bot.key.pem",
    "certificatePassword": ""
  },`  

A future enhancement will allow for more flexibility in how the certs can be configured.