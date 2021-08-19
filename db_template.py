from sqllex import *

template = {
    'detectives': {
        'id': [INTEGER, PRIMARY_KEY, UNIQUE, NOT_NULL],
        'nickname': [TEXT, UNIQUE, NOT_NULL],
        'discord_id': [INTEGER, UNIQUE, NOT_NULL],
        'points': [INTEGER, NOT_NULL, DEFAULT, 0],
        'week_points': [INTEGER, NOT_NULL, DEFAULT, 0],
        'salary': [INTEGER, NOT_NULL, DEFAULT, 0]
    }
}
