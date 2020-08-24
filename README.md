## Fish-shop bot
The project `telegram bot` for fish-shop web store. 
By the bot you can :
- Choose fish.
- Add fish to cart.
- Delete fish from cart.

All CRUD methods worked by API [documentation.elasticpath](https://documentation.elasticpath.com/commerce-cloud/docs/concepts/index.html)
## Get start
Install requirements from ```pip install requirements.txt```.

- Create default environment variables ```.env``` file.
- Create store in  [Elasticpath](https://www.elasticpath.com/)
- Create database on [RedisLabs](https://redislabs.com/)
- Create bot on [Telegram messenger](https://web.telegram.org/#/login)

Declare default environment variables in ```.env``` file:

-`STORE_ID`= elasticpath store ID.

-`CLIENT_ID`= elasticpath client ID.

-`CLIENT_SECRET`= elasticpath client secret.

-`ACCESS_TOKEN`= elasticpath access token.
    
-`TG_TOKEN`= telegram bot access token.

-`DATABASE_PASSWORD`= redislabs database password.

-`DATABASE_HOST`= redislabs database HOST.

-`DATABASE_PORT`= redislabs database PORT.

## Deploy on Heroku
Scripts must be specified In Procfile:
bot-tg: python3 tg_bot.py
Deploy git repository in Heroku server.
Carry over all variables from .env to Reveal Config Vars in heroku/settings.

## Run.
In cmd ```python tg_bot.py```.

## License
You may copy, distribute and modify the software.

## Motivation
The code is written for educational purposes - this is a lesson in the Python and web development course at [Devman] (https://dvmn.org).