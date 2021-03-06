# Wunderlist to Asana
<img src="https://dr0wv9n0kx6h5.cloudfront.net/664cb69d34d0ef040ff8a446e429bce8feb54b41/site/images/logo-big.png" height="128"><img src="http://virtualmarketingpro.com/app/webroot/img/vmp/arrows/Hand%20Drawn%20Arrow%20(37).png" height="128"><img src="https://freeter.io/embedding-web-apps/project-management/asana.png" height="128">

Export your Wunderlist content to Asana

# What you get
- Wunderlist lists --> Asana projects
- Wunderlist tasks --> Asana tasks

Preserved are:

  - subtasks,
  - due dates,
  - completion status,
  - notes,
  - comments.

# Usage:
1. Get `Python` and `pip` for your system (if in doubt, just install [Miniconda](https://docs.conda.io/en/latest/miniconda.html))
2. Create your Wunderlist backup (*Account Settings --> Create export*) - you'll need the `Tasks.json` file from the resulting zip
3. Create your Asana private access token (*My Profile Settings --> Apps --> Manage Developer Apps*)
4. Run the following:
```sh
$ pip install -r requirements.txt
$ python wunderlist_to_asana.py \
  <Wunderlist backup file> \
  <Asana token> \
  <Asana workspace name - must exist already> \
  [team_id - if your workspace is an organization]
```
`team_id` doesn't apply to you if your workspace is not an organization; if you're indeed part of an organization but don't know/don't care which team\_id should be used, the script will default to the 1st one of the teams you're on as retrieved from Asana.
