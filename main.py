from search_infoFUNCTIONS import (
    cleaner,
    content_info,
    downloader,
    episodes,
    season_episodes,
)
from server import server
from data import read, write
from bs4 import BeautifulSoup
from typing import Union
from telebot import TeleBot
from telebot.apihelper import ApiTelegramException
from telebot.types import (
    Message,
    User,
    Chat,
    ChatMember,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    InputMediaPhoto,
    InputMediaVideo,
    InputFile,
)
import os

bot_token = "6252205881:AAF4z5AtrOGLs0B5N5XtMOp6l1R7wczn6fY"
bot: TeleBot = TeleBot(token=bot_token)

# FUNCTIONS
def url(user_id: int) -> str:
  return f"https://t.me/r71il"

def subscription(user_id) -> Union[dict, None]:
    for channel in channels:
      try:
        member: ChatMember = bot.get_chat_member(channel, user_id)
        if member.status in ["creator", "member", "administrator"]:
            continue
      except:
        continue
      return {
            "channel" : channel
            }

#@bot.message_handler()
#def aihaga(message):
#  bot.reply_to(message,"البوت تحت الصيانه سيعمل خلال وقت قصير ⚙️")
# START
@bot.message_handler(
    commands=["start", "netflix"],
    func=lambda message: message.chat.id != dev["developer"]["id"]
)
def users_start(message: Message) -> None:
    user_id: int = message.from_user.id
    subscribed = subscription(user_id)

    if user_id not in users:
        users.append(user_id)
        write(dbs["users_db"], users)
        if others.get("options")["new_members_notice"]:
            caption: str = f"-> عضو جديد استخدم البوت 🔥\n\n-> ايدي : {user_id}\n-> يوزر : @{message.from_user. username}\n\n-> عدد الأعضاء الحاليين : {len(users)}"
            bot.send_message(
                dev["developer"]["id"],
                caption
            )

    if subscribed:
        subscribe_msg: str = f"🔰 | عذرا عزيزي عليك الإشتراك بقناة البوت أولا\n\n{subscribed['channel']}\n\nاشترك ثم ارسل: /start"
        bot.reply_to(
            message,
            subscribe_msg
        )
        return

    username: str = message.from_user.full_name
    main_text: str = f"""
 أهلا بك [{username}]({url(user_id)}) في بوت سينما العراق 
  من خلال هذا البوت يمكنك مشاهدة
  الأفلام والمسلسلات (الاجنبية-العربية-التركية)
  الانميات قريبًا

  🔰 | للبحث عن فلم اكتب كلمة ( فيلم ) بدون اقواس ثم اسم الفلم برسالة واحدة 

  🔰 | للبحث عن مسلسل اكتب كلمة ( مسلسل ) بدون اقواس ثم اسم المسلسل برسالة واحدة 


  🔰 | مثال :  فيلم The unseen | مسلسل see

  ‼️ اكتب اسم المسلسل او الفلم بالشكل الصحيح
 """
    main_keys = [[
        InlineKeyboardButton(bot.get_chat(dev["developer"]["id"]).first_name, url(dev["developer"]["id"])),
        InlineKeyboardButton(bot.get_chat(dev["channel"]["username"]).title, dev["channel"]["url"])
    ]]
    bot.send_video(
        chat_id= user_id, 
        video="https://f.top4top.io/m_2805azvu10.mp4",
        caption=main_text,
        reply_markup=InlineKeyboardMarkup(main_keys),
        reply_to_message_id=message.id,
        parse_mode="Markdown" 
    )

# MOVIES SEARCH
@bot.message_handler(
    func = lambda message : message.text.startswith(("فيلم", "فلم", "movie")) and message.from_user.id in users)
def movies(message: Message) -> None:
    user_id = message.from_user.id
    subscribed = subscription(user_id)
    if subscribed:
        subscribe_msg: str = f"🔰 | عذرا عزيزي عليك الإشتراك بقناة البوت أولا\n\n{subscribed['channel']}\n\nاشترك ثم ارسل: /start"
        bot.reply_to(
            message,
            subscribe_msg
        )
        return
    wait = bot.reply_to(message, "🔍چـار البحث")
    search: tuple = cleaner(message.text, "movie")
    if len(search) == 2:
        titles: list = [[InlineKeyboardButton(search[0][index], callback_data=f"movie-{message.text}-{index}")] for index  in range(0, len(search[0]))]
        bot.send_video(
            chat_id=user_id, 
            video="https://f.top4top.io/m_2805azvu10.mp4",
            caption="• نتائج البحث : ",
            reply_markup=InlineKeyboardMarkup(titles),
            reply_to_message_id=message.id,
            parse_mode="Markdown"
        )
        bot.delete_message(user_id, wait.id)
        return

    bot.delete_message(user_id, wait.id)
    bot.reply_to(message, search)

# MOVIES CALLBACKS
@bot.callback_query_handler(
    func = lambda callback: callback.data.startswith("movie-")
)
def choose_movie(callback: CallbackQuery) -> None:
    data: list = callback.data.split("-")
    movie: str = cleaner(data[1], "movie")[1][int(data[-1])]
    try:
        info: tuple = content_info(movie, "for one")
    except AttributeError:
        bot.reply_to(
            callback.message,
            "تنويه : احتمال هذا يكون مسلسل وليس فلمًا!"
        )
        return
    details: str = info[0]
    poster: str = info[1]
    watching: str = info[2]
    movie_keys = [
        [
            InlineKeyboardButton(bot.get_chat(dev["developer"]["id"]).first_name, url(dev["developer"]["id"]))
        ],
        [
            InlineKeyboardButton("المشاهده", watching),
            InlineKeyboardButton("التحميل", callback_data=f"download-movie-{data[1]}-{data[-1]}")
        ],
        [
            InlineKeyboardButton(bot.get_chat(dev["channel"]["username"]).title, dev["channel"]["url"])
        ],
        [
            InlineKeyboardButton("رچـوع ", callback_data=f"movies_result-{data[1]}")
        ]
    ]
    bot.edit_message_media(
        message_id=callback.message.id,
        chat_id=callback.message.chat.id,
        media=InputMediaPhoto(media=poster, caption=details, parse_mode="Markdown"),
        reply_markup=InlineKeyboardMarkup(movie_keys)
    )

@bot.callback_query_handler(
    func = lambda callback: callback.data.startswith("download-movie")
)
def download_movie(callback: CallbackQuery) -> None:
    data = callback.data.split("-")
    movie: str = cleaner(data[2], "movie")[1][int(data[3])]
    soup: BeautifulSoup = content_info(movie, "for one")[-1]
    urls, qualities = downloader(soup)
    download: list = [] 
    for i in range(0, len(urls), 2):
        if i +1 < len(urls):
            button1 = InlineKeyboardButton(qualities[i],  urls[i])
            button2 = InlineKeyboardButton(qualities[i+1],  urls[i+1])
            download.append([button1, button2])
        else:
            button = InlineKeyboardButton(qualities[i], urls[i])
            download.append([button])
    download.append([InlineKeyboardButton("رچـوع", callback_data=f"movie-{data[2]}-{data[3]}")])
    bot.edit_message_reply_markup(
        message_id=callback.message.id,
        chat_id=callback.from_user.id,
        reply_markup=InlineKeyboardMarkup(download)
    )

@bot.callback_query_handler(
    func=lambda callback: callback.data.startswith("movies_result")
)
def movies_result(callback: CallbackQuery) -> None:
    data = callback.data.split("-")[-1]
    search: tuple = cleaner(data, "movie")
    titles: list = [[InlineKeyboardButton(search[0][index], callback_data=f"movie-{data}-{index}")] for index  in range(0, len(search[0]))]
    bot.edit_message_media(
        message_id=callback.message.id,
        chat_id=callback.from_user.id,
        media=InputMediaVideo(media="https://f.top4top.io/m_2805azvu10.mp4", caption="• نتأئج البحث : " ),
        reply_markup=InlineKeyboardMarkup(titles)
    )

# SERIESES SEARCH
@bot.message_handler(
    func = lambda message : message.text.startswith(("مسلسل", "series")) and message.from_user.id in users)
def serieses(message: Message) -> None:
    user_id = message.from_user.id
    subscribed = subscription(user_id)
    if subscribed:
        subscribe_msg: str = f"🔰 | عذرا عزيزي عليك الإشتراك بقناة البوت أولا\n\n{subscribed['channel']}\n\nاشترك ثم ارسل: /start"
        bot.reply_to(
            message,
            subscribe_msg
        )
        return
    wait = bot.reply_to(message, "🔍چـار البحث")
    series : Union[str, None] = message.text
    search: tuple = cleaner(series, "series")
    if len(search) == 2:
        titles: list = [[InlineKeyboardButton(search[0][index], callback_data=f"series-{message.text}-{index}")] for index  in range(0, len(search[0]))]
        bot.send_video(
            chat_id=user_id, 
            video="https://f.top4top.io/m_2805azvu10.mp4",
            caption="• نتائج البحث : ",
            reply_markup=InlineKeyboardMarkup(titles),
            reply_to_message_id=message.id,
            parse_mode="Markdown"
        )
        bot.delete_message(user_id, wait.id)
        return

    bot.delete_message(user_id, wait.id)
    bot.reply_to(message, search)

# SERIESES CALLBACKS
@bot.callback_query_handler(
    func = lambda callback: callback.data.startswith("series-")
)
def choose_series(callback: CallbackQuery) -> None:
    data: list = callback.data.split("-")
    series: str = cleaner(data[1], "series")[1][int(data[2])]
    try:
        info: tuple = content_info(series, "series")
    except AttributeError:
        bot.reply_to(
          callback.message,
          "تنويه : احتمال ان يكون هذا  فلمًا وليس مسلسل!"
        )
        return
    details: str = info[0]
    poster: str = info[1]
    seasons: BeautifulSoup = info[-2]
    series_keys: list = []
    if seasons.find("div", { "class" : "List--Seasons--Episodes" }):
        seasons_amount: list = seasons.contents[0].find_all("a")
        for i in range(0, len(seasons_amount), 2):
            if i+1 < len(seasons_amount):
                button1 = InlineKeyboardButton(f"الموسم {i+1}", callback_data=f"season-{i}-{data[1]}-{data[-1]}")
                button2 = InlineKeyboardButton(f"الموسم {i+2}", callback_data=f"season-{i+1}-{data[1]}-{data[-1]}")
                series_keys.append([button1, button2])
            else:
                button = InlineKeyboardButton(f"الموسم {i+1}", callback_data=f"season-{i}-{data[1]}-{data[-1]}")
                series_keys.append([button])
    else:
        nums = episodes(seasons)[-1]
        for i in range(0, len(nums), 2):
            if i+1 < len(nums):
                button1 = InlineKeyboardButton(f"الحلقه {nums[i]}", callback_data=f"episode-{i}-{data[1]}-{data[-1]}")
                button2 = InlineKeyboardButton(f"الحلقه {nums[i+1]}", callback_data=f"episode-{i+1}-{data[1]}-{data[-1]}")
                series_keys.append([button1, button2])
            else:
                button = InlineKeyboardButton(f"الحلقه {nums[i]}", callback_data=f"episode-{i}-{data[1]}-{data[-1]}")
                series_keys.append([button])
    series_keys.append([InlineKeyboardButton("- العوده -", callback_data=f"serieses_result-{data[1]}-{data[-1]}")])
    bot.edit_message_media(
        message_id=callback.message.id,
        chat_id=callback.message.chat.id,
        media=InputMediaPhoto(media=poster, caption=details, parse_mode="Markdown"),
        reply_markup=InlineKeyboardMarkup(series_keys)
    )

@bot.callback_query_handler(
    func = lambda callback: callback.data.startswith("episode") and callback.from_user.id in users
)
def choose_episode(callback: CallbackQuery):
    data = callback.data.split("-")
    series: str = cleaner(data[2], "series")[-1][int(data[3])]
    info: tuple = content_info(series, "series")
    season: BeautifulSoup = info[-2]
    if len(data) > 4:
        episodess = season_episodes(season, int(data[-1]))[0]
        episodess.reverse()
        episode = episodess[int(data[1])].get("href")
        download_ep_data: str = f"download_ep-{data[1]}-{data[2]}-{data[3]}-{data[-1]}"
    else:
        episode = episodes(season)[0][int(data[1])]
        download_ep_data: str = f"download_ep-{data[1]}-{data[2]}-{data[3]}"
    info: tuple = content_info(episode, "for one")
    details: str = info[0]
    poster: str = info[1]
    watching: str = info[2]
    episode_keys = [
        [
            InlineKeyboardButton(bot.get_chat(dev["developer"]["id"]).first_name, url(dev["developer"]["id"]))
        ],
        [
            InlineKeyboardButton(" المشاهده", watching),
            InlineKeyboardButton(" التحميل ", callback_data=download_ep_data)
        ],
        [
            InlineKeyboardButton(bot.get_chat(dev["channel"]["username"]).title, dev["channel"]["url"])
        ],
        [
            InlineKeyboardButton("رچـوع ", callback_data=f"series_result-{data[2]}-{data[3]}")
        ]
    ]
    bot.edit_message_media(
        message_id=callback.message.id,
        chat_id=callback.message.chat.id,
        media=InputMediaPhoto(media=poster, caption=details, parse_mode="Markdown"),
        reply_markup=InlineKeyboardMarkup(episode_keys)
    )

@bot.callback_query_handler(
    func = lambda callback: callback.data.startswith("series_result")
)
def to_series(callback: CallbackQuery):
    choose_series(callback)

@bot.callback_query_handler(
    func=lambda callback: callback.data.startswith("season")
)
def season(callback: CallbackQuery):
    data: list = callback.data.split("-")
    series: tuple = cleaner(data[2], "series")[-1][int(data[-1])]
    seasons: tuple = content_info(series, "series")[-2]
    nums: list = season_episodes(seasons, int(data[1]))[1]
    nums.reverse()
    eps_keys: list = []
    for i in range(0, len(nums), 2):
        if i+1 < len(nums):
            button1 = InlineKeyboardButton(f"الحلقه {nums[i]}", callback_data=f"episode-{i}-{data[2]}-{data[-1]}-{data[1]}")
            button2 = InlineKeyboardButton(f"الحلقه {nums[i+1]}", callback_data=f"episode-{i+1}-{data[2]}-{data[-1]}-{data[1]}")
            eps_keys.append([button1, button2])
        else:
            button = InlineKeyboardButton(f"الحلقه {nums[i]}", callback_data=f"episode-{i}-{data[-2]}-{data[-1]}-{data[1]}")
            eps_keys.append([button])
    eps_keys.append([InlineKeyboardButton("- العوده -", callback_data=f"series_result-{data[2]}-{data[-1]}")])
    bot.edit_message_reply_markup(
        chat_id=callback.from_user.id, 
        message_id=callback.message.id,
        reply_markup=InlineKeyboardMarkup(eps_keys)
    )

@bot.callback_query_handler(
  func=lambda callback: callback.data.startswith("download_ep")
)
def download_ep(callback: CallbackQuery):
    data = callback.data.split("-")
    series: str = cleaner(data[2], "series")[-1][int(data[3])]
    info: tuple = content_info(series, "series")
    season: BeautifulSoup = info[-2]
    if len(data) > 4:
        episode = season_episodes(season, int(data[-1]))[0][int(data[1])].get("href")
        back_to_ep: str = f"episode-{data[1]}-{data[2]}-{data[3]}-{data[-1]}"
    else:
        episode = episodes(season)[0][int(data[1])]
        back_to_ep: str = f"episode-{data[1]}-{data[2]}-{data[3]}"
    info: tuple = content_info(episode, "for one")
    urls, qualities = downloader(info[-1])
    download: list = [] 
    for i in range(0, len(urls), 2):
        if i +1 < len(urls):
            button1 = InlineKeyboardButton(qualities[i],  urls[i])
            button2 = InlineKeyboardButton(qualities[i+1],  urls[i+1])
            download.append([button1, button2])
        else:
            button = InlineKeyboardButton(qualities[i], urls[i])
            download.append([button])
    download.append([InlineKeyboardButton("- العوده -", callback_data=back_to_ep)])
    bot.edit_message_reply_markup(
        message_id=callback.message.id,
        chat_id=callback.from_user.id,
        reply_markup=InlineKeyboardMarkup(download)
    )

@bot.callback_query_handler(
    func=lambda callback: callback.data.startswith("serieses_result")
)
def serieses_result(callback: CallbackQuery) -> None:
    data: list = callback.data.split("-")

    series: tuple = cleaner(data[1], "series")
    titles: list = [[InlineKeyboardButton(series[0][index], callback_data=f"series-{data[1]}-{index}")] for index  in range(0, len(series[0]))]
    bot.edit_message_media(
        chat_id=callback.from_user.id, 
        message_id=callback.message.id,
        media=InputMediaVideo(media="https://f.top4top.io/m_2805azvu10.mp4", caption="● نتائج البحث : "),
        reply_markup=InlineKeyboardMarkup(titles)
    )

# FOR ME
@bot.message_handler(
    func = lambda message: "صفحه" in message.text and message.from_user.id == dev["developer"]["id"],
)
def page(message: Message):
    search: tuple = cleaner(message.text, "movie")
    urls = search[1]
    text = "\n\n".join(urls)
    bot.reply_to(
      message,
      text
    )

# Broadcasting
@bot.message_handler(
    func = lambda message: message.text == "اذاعه" and message.from_user.id == dev["developer"]["id"],
)
def setup_cast(message: Message) -> None:
    global casted
    casted  = False
    bot.reply_to(
        message,
        "الإذاعه جاهزه 👀"
    )

@bot.message_handler(
    func = lambda message: not casted and message.from_user.id == dev["developer"]["id"],
    content_types=["text", "audio", "voice", "video", "document", "photo"]
)
def broadcasting(message: Message) -> None:
    global casted
    casted = True
    denied: list = []
    for user in users:
        try:
            bot.copy_message(
                chat_id=user,
                from_chat_id=message.from_user.id,
                message_id=message.id
            )
        except ApiTelegramException:
          denied.append(str(user))
          continue
    denied_users: str = "\n- ".join(denied) if len(denied) > 0 else "تم الإرسال للجميع."
    bot.reply_to(
      message,
      f"تمت الإذاعه بنجاح.\n\nعدد المحظورين : {len(denied)}"
    )
@bot.message_handler(
    func = lambda message: "اقتراح" in message.text and message.from_user.id == dev["developer"]["id"],
    content_types=["text"]
)
def suggest(message: Message) -> None:
    info = content_info(message.text.split(" ")[-1], "for one")
    details: str = info[0]
    poster: str = info[1]
    watching: str = info[2]
    download: tuple = downloader(info[-1])
    urls: list = download[0]
    qualities: list = download[1]
    content_keys = [
        [
            InlineKeyboardButton(bot.get_chat(dev["developer"]["id"]).first_name, url(dev["developer"]["id"])),
            InlineKeyboardButton(bot.get_chat(dev["channel"]["username"]).title, dev["channel"]["url"])
        ],
        [
            InlineKeyboardButton("- المشاهده -", watching),
        ],
        [
            InlineKeyboardButton("- التحميل -", callback_data="imagine")
        ]
    ]

    for i in range(0, len(urls), 2):
        if i+1 < len(urls):
            button1 = InlineKeyboardButton(qualities[i], urls[i])
            button2 = InlineKeyboardButton(qualities[i+1], urls[i+1])
            content_keys.append([button1, button2])
        else:
            button = InlineKeyboardButton(qualities[i], urls[i])
            content_keys.append([button])
    denied: list = []
    for user in users:
        try:
            bot.send_photo(
                chat_id=user, 
                photo=poster,
                caption=details,
                reply_markup=InlineKeyboardMarkup(content_keys)
              )
        except ApiTelegramException as e:
          denied.append(str(user))
          continue

    denied_users = "\n- ".join(denied) if len(denied) > 0 else "تم الإرسال للجميع."
    bot.reply_to(
        message,
        f"تمت الإذاعه بنجاح.\n\nعدد المحظورين : {len(denied)}"
        )

# ADMINISTRATOR
@bot.message_handler(
    commands=["start"], 
    chat_types=["private"], 
    func=lambda message: message.from_user.id == dev["developer"]["id"])
def admin_start(message: Message) -> None:
    user_id: int = message.from_user.id
    admin: Chat = bot.get_chat (user_id)
    admin_name: str = admin.first_name

    caption: str = f"-> مرحبا عزيزي الأدمن ( `{admin_name}` )\n\n-> احصائيات: \n\n-> الأعضاء : {len(users)}\n-> المحظورين : {len(banned.keys())}"
    keys: list = keyboard()
    bot.send_message(
        chat_id=message.chat.id,
        text=caption,
        reply_markup=InlineKeyboardMarkup(keys),
        parse_mode="Markdown"
    )

def keyboard() -> list:
    keys: list = [
    [
        InlineKeyboardButton( "- تغيير اسم البوت -", callback_data="set-bot-name") # DONE
    ],
    [
        InlineKeyboardButton(
            "- التوجيه من الأعضاء ✅️ -" if others.get("options")["forward_from_users"] else "- التوجيه من الأعضاء ❌️ -",
             callback_data="forward_from_users"), # DONE
        InlineKeyboardButton(
            "- تنبيه الأعضاء الجدد ✅️ -" if others.get("options")["new_members_notice"] else "- تنبيه الأعضاء الجدد ❌️ -", 
            callback_data="new_members_notice") # DONE
    ],
    [
        InlineKeyboardButton("- إضافة قناه -", callback_data="add_channel"), # DONE
        InlineKeyboardButton("- حذف قناه -", callback_data="remove_channel") # DONE
    ],
    [
        InlineKeyboardButton("- التخزين -", callback_data="send_storage") # DONE
    ]
    ]
    return keys

@bot.callback_query_handler(
    func=lambda callback: callback.data == "send_storage" and callback.from_user.id == dev["developer"]["id"])
def send_storage(callback: CallbackQuery) -> None:
    path: str = "database"
    files = os.listdir(path)
    for file in files:
        file_path = os.path.join(path, file)
        bot.send_document(
            callback.from_user.id,
            InputFile(file_path)
        )

@bot.callback_query_handler(
    func=lambda callback: callback.data in others["options"].keys() and callback.from_user.id == dev["developer"]["id"])
def redefine_attrs(callback: CallbackQuery):
    past = others["options"][callback.data]
    others["options"][callback.data] = True if not past else False
    write(dbs["others_db"], others)
    keys: list = keyboard()
    bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id, 
        message_id=callback.message.id,
        reply_markup=InlineKeyboardMarkup(keys) 
    )

@bot.callback_query_handler(
    func= lambda callback: callback.data == "add_channel" and callback.from_user.id == dev["developer"]["id"])
def add_channel(callback: CallbackQuery):
    global removed, added
    removed, added = True, False
    founded = "\n".join(channels)
    bot.send_message(
        callback.message.chat.id,
        f"-> القنوات الحاليه : \n\n{founded}\n\n-> أرسل معرف القناه  ليتم اضافتها 🔗",
    )

@bot.message_handler(
    func = lambda message: message.text.startswith("@") and not added and message.from_user.id == dev["developer"]["id"],
    chat_types=["private"]
    )
def receive_channel(message: Message):
    global added
    added = True
    channel = message.text
    try:
        bot.get_chat(channel)
        channels.append(channel)
    except:
        bot.reply_to(
            message,
            "لم يتم ايجاد هذه الدردشه."
        )
        return
    write(dbs["channels_db"], channels)
    founded = "\n".join(channels)
    bot.reply_to(
        message,
        f"-> تم إضافة القناه.\n\nالقنوات الحاليه : \n{founded}"
    )

@bot.callback_query_handler(
    func= lambda callback: callback.data == "remove_channel" and callback.from_user.id == dev["developer"]["id"])
def remove_channel(callback: CallbackQuery):
    global removed, added
    removed, added = False, True
    founded = "\n".join(channels)
    bot.send_message(
        callback.message.chat.id,
        f"-> القنوات الحاليه : \n\n{founded}\n\n-> أرسل معرف القناه ليتم حذفها 🔗",
    )

@bot.message_handler(
    func = lambda message: message.text.startswith("@") and not removed and message.from_user.id == dev["developer"]["id"],
    chat_types=["private"]
    )
def receive_channel(message: Message):
    global removed
    removed = True
    channel = message.text
    try:
        bot.get_chat(channel)
        channels.remove(channel)
    except:
        bot.reply_to(
            message,
            "لم يتم ايجاد هذه الدردشه."
        )
        return
    write(dbs["channels_db"], channels)
    founded = "\n".join(channels)
    bot.reply_to(
        message,
        f"-> تم حذف القناه.\n\nالقنوات الحاليه : \n{founded}"
    )

@bot.callback_query_handler(
    func=lambda callback: callback.data == "set-bot-name" and callback.from_user.id == dev["developer"]["id"])
def set_bot_name(callback: CallbackQuery):
    global changed
    changed = False
    bot.send_message(
        chat_id=callback.message.chat.id, 
        text="أرسل الاسم الجديد 🔗",
    )

@bot.message_handler(
    func= lambda message: message.chat.id == dev["developer"]["id"] and not changed)
def set_new_name(message: Message):
    global changed
    changed = True
    past_name: str = bot.get_me().full_name

    if past_name == message.text:
        bot.reply_to(
            message,
            "هذا نفس الإسم الحالي 😊"
            )
        return

    try:
        bot.set_my_name(message.text)
    except ApiTelegramException as E:
        seconds = float(str(E).split('after')[-1])
        hours = seconds / 3600
        formatted_hours = "{:.2f}".format(hours)
        bot.reply_to(
            message,
            f"-> لا يمكنك تغيير الإسم مجددا إلا بعد {str(E).split('after')[-1]} ثانيه أي بعد {formatted_hours} ساعه."
        )
        return

    new_name = bot.get_me().full_name
    caption: str  =  f"-> تم تغيير إسم البوت من {past_name} إلى {new_name}" 

    bot.reply_to(
        message,
        caption
    )

@bot.message_handler(
    func= lambda message: message.reply_to_message and message.from_user.id == dev["developer"]["id"],
    chat_types=["private"],
    content_types=["text", "audio", "voice", "video", "document", "photo"])
def reply(message: Message):
    try:
        user_id = message.reply_to_message.forward_from.id
    except AttributeError:
      bot.reply_to(
        message,
        "قام هذا المستخدمه بإخفاء معلوماته!"
      )
      return
    message_id = message.id
    bot.copy_message(
        chat_id=user_id,
        from_chat_id=message.chat.id, 
        message_id=message_id,
        )

@bot.message_handler(
  commands=['help']
)
def helpness(message: Message):
  bot.reply_to(
    message,
    text = f"🔰 | [{message.from_user.first_name}](tg://openmessage?user_id={message.from_user.id})\n🔰 | استخدم كلمة (`فيلم`) قبل اسم الفيلم\n🔰 | او كلمة (`مسلسل`) قبل اسم المسلسل",
    parse_mode="Markdown"
  )


@bot.message_handler(
    func= lambda message: others["options"]["forward_from_users"] and message.from_user.id != dev["developer"]["id"],
    chat_types=["private"],
    content_types=["text", "audio", "voice", "video", "document", "photo"])
def forward_from_users(message: Message):
    bot.forward_message(
        dev["developer"]["id"],
        from_chat_id = message.from_user.id,
        message_id = message.id
    )



if __name__ == "__main__":
    added, removed, changed, casted = True, True, True, True
    dbs = {
        "developer_db" : "database/mainINFO.json",
        "users_db" : "database/users.json",
        "banned_db" : "database/banned.json",
        "channels_db" : "database/channels.json",
        "others_db" : "database/others.json",
    }
    dev: dict = read(dbs["developer_db"])
    users: list = read(dbs["users_db"])
    channels: list = read(dbs["channels_db"])
    banned: dict = read(dbs["banned_db"])
    others: dict = read (dbs["others_db"])
    server()
    bot.infinity_polling()