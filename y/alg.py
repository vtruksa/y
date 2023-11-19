from django.utils.timesince import timesince

from post.models import Post, Tag
from user.models import UserProfile

def PostVisibility(posts = None):
#    print('Calculating post visibility for: '+ str(posts) + '\toriginal: ' + str(posts[0]._visibility))
    prog = 0

    if posts is None:
        posts = Post.objects.all()

    # TODO once post times are adjusted, consider the age of posts as well
    for p in posts:
        # Adds big bonus visibility according to the age of the post, when the post is older than one month
        # this bonus gets to its lowest value - 1, where it stays forever, no matter the post age
        age = timesince(p.created).split(',')
#        print(age)
        
        if 'week' in age[0]:
            # age[0][0] corresponds to the number of weeks, age[1][1] to the number of days thanks to the space
            age = int(age[0][0])*7 
            try:
                alg += int(age[1][1])
            except: pass
        elif 'days' in age[0]: age = int(age[0][0])
        elif 'hours' in age[0] or 'minutes' in age[0] or 'seconds' in age[0]: age = 0
        else: age = 31
        p._visibility = (0.5*len(p.liked.all()) + 0.7*len(Post.objects.filter(reply_to=p, just_a_share=True)) + 1*len(Post.objects.filter(reply_to=p, just_a_share=False)) + 1)*(31-age)
        p.save()
        UserVisibility([UserProfile.objects.get(user=p.author)])
        for t in p.tags_new.all():
            TagVisibility([t])
#        print('new: ' + str(p._visibility))
        prog += 1
        print("Calculating post visibility, current progress is: " + str(100*prog/len(posts)))

def TagVisibility(tags = None):
#    print('Calculating tag visibility for: '+ str(tags) + '\toriginal: ' + str(tags[0]._visibility))
    prog = 0

    if tags is None:
        tags = Tag.objects.all()

    # TODO once post times are adjusted, consider the age of posts as well
    for t in tags:
        vis = 0
        for p in t.posts.all():
            vis += p._visibility
        t._visibility = vis
        t.save()
        prog += 1
        print("Calculating tag visibility, current progress is: " + str(100*prog/len(tags)))
#        print('new: ' + str(t._visibility))

def UserVisibility(users = None):
#    print('Calculating user visibility for: '+ str(users) + '\toriginal: ' + str(users[0]._visibility))
    prog = 0

    if users is None:
        users = UserProfile.objects.all()

    for u in users:
        vis = 0
        for p in u.posts.all():
            vis += p._visibility
        vis += len(u.followers.all())
        u._visibility = vis
        u.save()
        prog += 1
#        print('new: ' + str(u._visibility))
        print("Calculating user visibility, current progress is: " + str(100*prog/len(users)))