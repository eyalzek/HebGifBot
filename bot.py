import requests
import telepot
from telepot.delegate import per_inline_from_id, create_open, pave_event_space
from yandex_translate import YandexTranslate
from ConfigParser import ConfigParser


class GifBot(telepot.helper.InlineUserHandler, telepot.helper.AnswererMixin):
    def __init__(self, *args, **kwargs):
        super(GifBot, self).__init__(*args, **kwargs)
        self.init_translator()

    def init_translator(self):
        self.translator = init_service(load_key("translate"))

    def construct_choice(self, data):
        return {
            "type": "gif",
            "id": data["id"],
            "gif_url": data["url"],
            "gif_width": data["width"],
            "gif_height": data["height"],
            "thumb_url": data["thumb_url"]
        }

    def on_inline_query(self, msg):
        def compute_answer():
            query_id, from_id, query_string = telepot.glance(msg, flavor="inline_query")
            print(self.id, ":", "Inline Query:", query_id, from_id, query_string)
            translated = translate_query(self.translator, query_string)
            gifs = get_gifs(translated)
            return map(self.construct_choice, gifs)

        self.answerer.answer(msg, compute_answer)

    def on_chosen_inline_result(self, msg):
        from pprint import pprint
        pprint(msg)
        result_id, from_id, query_string = telepot.glance(msg, flavor="chosen_inline_result")
        print(self.id, ":", "Chosen Inline Result:", result_id, from_id, query_string)

def load_key(section):
    c = ConfigParser()
    c.read(".secrets")
    return c.get(section, "api_key")

def init_service(api_key):
    return YandexTranslate(api_key)

def translate_query(s, q):
    try:
        return s.translate(q, "he-en")["text"][0]
    except IndexError:
        print("translation error.")
    except KeyError:
        print("translation error.")

def construct_gif_option(gif):
    return {
        "id": gif["id"],
        "thumb_url": gif["images"]["downsized_still"]["url"],
        "url": gif["images"]["downsized"]["url"],
        "height": int(gif["images"]["downsized"]["height"]),
        "width": int(gif["images"]["downsized"]["width"])
    }

def get_gifs(q):
    r = requests.get("http://api.giphy.com/v1/gifs/search?q=%s&api_key=dc6zaTOxFJmzC"
        % q.replace(" ", "+"))
    return map(construct_gif_option, r.json()["data"])

def get_request():
    pass

def on_inline_query(msg):
    query_id, from_id, query_string = telepot.glance(msg, flavor="inline_query")
    print ("Inline Query:", query_id, from_id, query_string)

def main():
    bot = telepot.DelegatorBot(load_key("telegram"), [
        pave_event_space()(
            per_inline_from_id(), create_open, GifBot, timeout=10),
    ])
    bot.message_loop(run_forever='Listening ...')

if __name__ == "__main__":
    main()
