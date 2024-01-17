# -*- coding: utf-8 -*-
import openai
from dotenv import load_dotenv
import os


def image_gpt():
    photo_test = "https://cdn.discordapp.com/attachments/1041539813821653022/1176023457763430480/image.png" # net apple
    photo_test_1 = "https://media.discordapp.net/attachments/1041539813821653022/1176716574082744511/img_0.jpg" # big apple
    test_1 = "https://cdn.discordapp.com/attachments/1041539813821653022/1176718220779081869/image.png" # half apple
    test_2 = "https://cdn.discordapp.com/attachments/1041539813821653022/1176718025072836701/img_1600.jpg" # no apple
    test_3 = "https://cdn.discordapp.com/attachments/1041539813821653022/1176747739145576559/image.png" # black and white apple
    photo = "https://tondabayashi.sakura.ne.jp/drone/img.jpg" #drone photo
    load_dotenv()
    openai.api_key =os.environ['OPENAI_API_KEY'] 
    completion = openai.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[ #りんごが端に写っても反応するので、中央に写ったらとか発展出来てもいい、>プロンプト
           {
                "role": "user",
                "content": [
                    {"type": "text", "text": "if you can see a apple in the picture, just say 「apple」 back. if you do not see a apple in the picture , just say 「no」 back."},
                    {
                        "type": "image_url", 
                        "image_url": photo,
                    },
                ],
            },
        ],
    )
    gpt_return = completion.choices[0].message.content
    return gpt_return

# 仮実行
# image_gpt() 

def main():
    message = 0
    # image_gpt(2)

if __name__ == "__main__":
    main()