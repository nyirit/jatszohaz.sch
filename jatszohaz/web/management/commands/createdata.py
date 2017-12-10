from django.core.management.base import BaseCommand
from web.models import JhUser, GameGroup, GamePiece, GamePack


class Command(BaseCommand):
    help = "Create data for testing. It will PERMANENTLY " \
           "delete test users and ALL EXISTING GameGroup, GamePiece and GamePack objects!"

    users = (
        {'username': "admin",
         'password': "1234",
         'mobile': "+0000303030",
         'room': "1910",
         'email': "test@jh.hu",
         'first_name': "Admin",
         'last_name': "Elek",
         'is_superuser': True,
         'is_staff': True},
        {'username': "user",
         'password': "1234",
         'mobile': "+0000303030",
         'room': "1910",
         'email': "test@jh.hu",
         'first_name': "Teszt",
         'last_name': "Elek",
         'is_superuser': False,
         'is_staff': False},
        {'username': "user2",
         'password': "1234",
         'mobile': "+0000303031",
         'room': "1911",
         'email': "test2@jh.hu",
         'first_name': "Teszt2",
         'last_name': "Elek",
         'is_superuser': False,
         'is_staff': False},
    )

    def handle(self, *args, **options):
        self.__delete_games()
        self.__create_users()
        self.__create_games()
        self.stdout.write(self.style.SUCCESS('DONE'))

    def __create_users(self):
        self.__delete_users()
        for user in self.users:
            JhUser.objects.create_user(
                username=user['username'],
                password=user['password'],
                mobile=user['mobile'],
                room=user['room'],
                email=user['email'],
                first_name=user['first_name'],
                last_name=user['last_name'],
                is_staff=user['is_staff'],
                is_superuser=user['is_superuser']
            ).save()
            self.stdout.write('%s user created.' % user['username'])
        pass

    def __delete_users(self):
        for user in self.users:
            try:
                u = JhUser.objects.get(username=user['username'])
                u.delete()
                self.stdout.write('%s user deleted.' % user['username'])
            except JhUser.DoesNotExist:
                pass

    def __create_games(self):
        owner = JhUser.objects.get(username='user')

        gg1 = GameGroup.objects.create(
            name="Bang",
            description="Bang Bang Bang!",
            short_description="Bang bang!"
        )
        gg1.save()
        GamePiece.objects.create(
            owner=owner,
            game_group=gg1,
            notes="Bang 0. It belongs to 'user'.",
            priority=0
        ).save()
        GamePiece.objects.create(
            game_group=gg1,
            notes="Bang 1. It belongs to nobody.",
            priority=1
        ).save()
        GamePiece.objects.create(
            game_group=gg1,
            notes="Bang 2. It belongs to nobody.",
            priority=2
        ).save()

        gg2 = GameGroup.objects.create(
            name="Catan",
            description="Catan descripton!",
            short_description="Catan short"
        )
        gg2.save()
        GamePiece.objects.create(
            owner=owner,
            game_group=gg2,
            notes="Catan 0. It belongs to 'user'.",
            priority=0
        ).save()
        GamePiece.objects.create(
            game_group=gg2,
            notes="Catan 1. It belongs to nobody.",
            priority=1
        ).save()
        GamePiece.objects.create(
            game_group=gg2,
            notes="Catan 2. It belongs to nobody.",
            priority=2
        ).save()

        gp = GamePack.objects.create(name="Bang-Catan", creator=owner, active=True)
        gp.games.add(gg1)
        gp.games.add(gg2)
        gp.save()
        gp = GamePack.objects.create(name="Bang", creator=owner, active=True)
        gp.games.add(gg1)
        gp.save()
        GamePack.objects.create(name="Empty", creator=owner, active=True).save()
        self.stdout.write('GameGroups, GamePieces and GamePack created.')

    def __delete_games(self):
        GamePiece.objects.all().delete()
        GameGroup.objects.all().delete()
        GamePack.objects.all().delete()
