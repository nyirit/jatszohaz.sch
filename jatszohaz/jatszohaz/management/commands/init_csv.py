import csv
from urllib.request import urlopen
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.management.base import BaseCommand
from inventory.models import GameGroup, GamePiece, InventoryItem
from jatszohaz.models import JhUser


class Command(BaseCommand):
    help = "Init database from csv file."

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            help='Csv input file'
        )

        parser.add_argument(
            '--delete-all',
            help='Irreversibly removes ALL data regarding games.',
            dest="delete",
            action='store_true'
        )

    def write(self, txt):
        self.stdout.write(txt)

    def __handle_row(self, row):
        # get columns
        game_group = row[0]
        game_piece_note = row[1]
        # extension = row[2] TODO
        priority = row[3] or '0'
        image_url = row[4] or 'http://www.bsmc.net.au/wp-content/uploads/No-image-available.jpg'
        short_desc = row[5]
        long_desc = row[6]
        player_number = row[7]
        playtime = row[8]
        rules = row[9]
        missing = row[10]
        damage = row[11]
        playable = row[12]
        rentable = row[13]

        gg, created = GameGroup.objects.get_or_create(name=game_group)

        if created:
            gg.description = long_desc
            gg.short_description = short_desc[:100]
            gg.players = player_number
            gg.playtime = playtime

            image_url = image_url
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urlopen(image_url).read())
            img_temp.flush()

            gg.image.save("Picture", File(img_temp))
            gg.save()

        gp = GamePiece.objects.create(
            game_group=gg,
            notes=game_piece_note,
            priority=priority,
            rentable=rentable,
        )
        gp.save()

        InventoryItem.objects.create(
            user=JhUser.objects.first(),
            game=gp, playable=playable,
            missing_items=missing + damage,
            rules=rules
        ).save()

        self.write(self.style.SUCCESS("Added: %s - %s" % (game_group, game_piece_note)))

    def handle(self, *args, **options):
        self.write(self.style.WARNING("Input file: %s" % options['file']))
        self.write(self.style.WARNING("Delete everything: %s" % options['delete']))

        if options['delete']:
            GamePiece.objects.all().delete()
            self.write(self.style.SUCCESS('GamePiece object deleted.'))
            GameGroup.objects.all().delete()
            self.write(self.style.SUCCESS('GameGroup object deleted.'))

        try:
            with open(options['file'], 'rt') as csvfile:
                reader = csv.reader(csvfile, delimiter=",")
                reader.__next__()  # skip first line
                for row in reader:
                    try:
                        self.__handle_row(row)
                    except Exception as e:
                        self.write(self.style.ERROR("%s\nSomething bad happend at row %s" % (e, row)))
                        return
        except FileNotFoundError:
            self.write(self.style.ERROR("No such file: %s" % options['file']))
