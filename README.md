# Secret Santa

Make people fill in your Google Form, download the results in CSV and parse it using following command:
```
python3 parse_google_form.py --form_csv FORM.csv --output_players_info_json PLAYERS.json
```

Run the Secret Santa solver without sending emails to check if everythig is working fine:
```
python3 main.py --players_json PLAYERS.json 
```

Write your mail inside MAIL_BODY.txt and finally run the Secret Santa and send emails:
```
python3 main.py --players_json PLAYERS.json --mail_address MY_MAIL@gmail.com --mail_pwd MY_APP_PASSWORD --mail_txt MAIL_BODY.txt
```

Have a look at my Medium articles explaining how it works:
- [Let me help you organize your best Secret Santa ever](https://medium.com/@thom01.rouch/let-me-help-you-organize-your-best-secret-santa-ever-c0fef5e61ba2)

- [Secret Santa from a Google Form](https://medium.com/@thom01.rouch/secret-santa-from-a-google-form-32841566d984)
