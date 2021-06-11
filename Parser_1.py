"""Собираем фото со стены ВК"""

import os
import requests
import json
from vk_data import Data


def get_wall_posts(group_name, count_post):
    token = Data.getter()
    url = f"https://api.vk.com/method/wall.get?domain={group_name}&count={count_post}&access_token={token}&v=5.52"
    req = requests.get(url)
    src = req.json()
    posts = src["response"]["items"]
    # print(posts) Промежуточная проверка.
    return src, posts


def create_dir(group_name, src):
    """Проверяем существует ли директория с именем группы"""
    if os.path.exists(f"{group_name}"):
        print(f"Директория группы с именем {group_name} уже существует")
    else:
        os.mkdir(group_name)  # Создаём директорию в нашем проекте.

    """ Сохраняем в JSON файл """
    with open(f"{group_name}/{group_name}", 'w', encoding='utf-8') as file:
        json.dump(src, file, indent=4, ensure_ascii=False)


def get_data_from_posts(posts):
    """ Вытаскиваем данные из постов """
    for post in posts:
        post_id = post["id"]
        print(f"Отправляем пост с id {post_id}")
        try:
            if "attachments" in post:
                post = post["attachments"]

                if post[0]["type"] == "photo":
                    photo_quality = ["photo_2560", "photo_1280", "photo_807", "photo_604", "photo_130",
                                     "photo_75"]
                    # если в посте одно фото, то забираем его
                    if len(post) == 1:
                        for pq in photo_quality:
                            if pq in post[0]["photo"]:
                                post_photo = post[0]["photo"][pq]
                                print(post_photo)
                                break
                    # иначе пробегаем по всем фото в посте
                    else:
                        for post_item_photo in post:
                            if post_item_photo["type"] == "photo":
                                for pq in photo_quality:
                                    if pq in post_item_photo["photo"]:
                                        post_photo = post_item_photo["photo"][pq]
                                        print(post_photo)
                                        break

        except IOError:
            print(f"Что-то пошло не так с постом id {post_id}!!!")


def get_posts(group_name, posts):
    """ Создаём список ID постов """
    fresh_posts_id = []
    for fresh_post_id in posts:
        fresh_post_id = fresh_post_id["id"]
        fresh_posts_id.append(fresh_post_id)
    # print(fresh_posts_id) #Промежуточная проверка, на выходе получаем список id.

    """Проверяем, существует ли файл. Если файла не существует,
       значит парсим группу первый раз и отправляем посты.
       Если существует, то проверяем посты и отправляем только новые."""

    if not os.path.exists(f"{group_name}/exist_posts_{group_name}.txt"):
        print('Файла с ID не существует, создаём новый.')

        with open(f"{group_name}/exist_posts_{group_name}.txt", 'w') as file:
            for item in fresh_posts_id:
                file.write(str(item) + '\n')

        get_data_from_posts(posts)
    else:
        print('Файл с ID уже существует, проверяем новые посты.')
        count = 0
        old_posts_id = []
        new_posts_id = []
        try:
            with open(f"{group_name}/exist_posts_{group_name}.txt", 'r') as file:
                for item in file:
                    item = item.replace("\n", "")
                    old_posts_id.append(int(item))

            with open(f"{group_name}/exist_posts_{group_name}.txt", 'a') as file:
                for pos in fresh_posts_id:
                    if pos not in old_posts_id:
                        file.write(str(pos) + '\n')
                        new_posts_id.append(pos)
                        count += 1
            if count > 0:
                get_data_from_posts(posts)
            else:
                print("Новых постов нет.")
        except (IOError, EOFError):
            print("Не удалось открыть файл для проверки новых постов")


def main():
    group_name = input('Введите имя группы: ')
    count_post = input("Введите количество постов : ")
    try:
        (src, posts) = get_wall_posts(group_name, count_post)
    except Exception:
        print("Что-то пошло не так !!!")
    else:
        try:
            create_dir(group_name, src)
        except OSError:
            print("Ошибка в имени файла!!!")
        else:
            get_posts(group_name, posts)


if __name__ == '__main__':
    main()
