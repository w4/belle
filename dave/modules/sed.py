# -*- coding: utf-8 -*-
"""Pass any messages beginning with 'sed' to GNU sed."""
import dave.module
import dave.config
from twisted.words.protocols.irc import assembleFormattedText, attributes as A
import re

@dave.module.help("Syntax: s/find/replace/flags", "sed")
@dave.module.match(r"^((s|y)(/|\||!)(.*?)(\3)(.*?)(\3)([gIi]+)?)$")
@dave.module.priority(dave.module.Priority.HIGHEST)
def sed(bot, args, sender, source):
    key = "msg:{}:{}".format(source, sender)

    for i, msg in enumerate(dave.config.redis.lrange(key, 0, -1)):
        flags = list(args[7]) if args[7] else []
        f = re.UNICODE

        if 'I' in flags or 'i' in flags:
            f = f | re.IGNORECASE

        try:
            # bold replacements
            replace = re.sub(args[3], "\x02{}\x0F".format(args[5]),
                             msg, count=0 if 'g' in flags else 1, flags=f)
        except Exception as e:
            bot.reply(source, sender,
                      "There was a problem with your sed command: {}".format(str(e)))
            return

        if replace.strip() != msg:
            msg = replace.strip()
            bot.msg(source, "<{}> {}".format(sender, msg))
            dave.config.redis.lset(key, i, msg)
            return


@dave.module.match(r"(.*)")
@dave.module.priority(dave.module.Priority.LOWEST)
def update_cache(bot, args, sender, source):
    key = "msg:{}:{}".format(source, sender)
    dave.config.redis.lpush(key, args[0])
    dave.config.redis.ltrim(key, 0, 2)