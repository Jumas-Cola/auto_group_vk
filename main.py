from User import User
import time


if __name__ == '__main__':
    user = User()
    post = user.get_random_post()
    user.make_post(post['attachments'], post['donor_id'])
    if user.repost:
        user.repost_last_post()
    if user.add_friends:
        user.add_all_to_friends()
    if user.del_requests:
        user.friends_deny_request()
    if user.sqlog:
        user.add_in_db(f'{post["donor_id"]}_{post["donor_post_id"]}')
