# coding: utf-8

import random
import string
import datetime
import time

import factory
from django.core.management.base import BaseCommand
from django.db.models import signals
from registration.models import RegistrationProfile

from django.contrib.auth.models import User
from accounts.models import UserAccount

from organizations.models import Organization, Facility, Workplace, Task
from tests.factories import ShiftHelperFactory, ShiftFactory, FacilityFactory, PlaceFactory, OrganizationFactory, \
    NewsEntryFactory, TaskFactory, UserAccountFactory
from scheduler.models import Shift
from places.models import Region, Area, Place, Country

HELPTOPICS = ["Jumper", "Translator", "Clothing Room", "Womens Room",
              "Donation Counter", "Highlights"]
LOREM = "Lorem tellivizzle dolizzle bling bling amizzle, mah nizzle adipiscing" \
        " elit. Nullam doggy velizzle, pizzle volutpizzle, suscipizzle" \
        " quizzle, gangsta vizzle, i'm in the shizzle. Pellentesque boom" \
        " shackalack for sure. The bizzle erizzle. Fusce izzle dolor " \
        "dapibus shit tempizzle dang. Sure pellentesque nibh izzle turpis." \
        " Vestibulum izzle tortor. Pellentesque ma nizzle rhoncizzle " \
        "bling bling. In hizzle habitasse i'm in the shizzle dictumst. " \
        "Bizzle dapibizzle. Curabitizzle tellizzle urna, pretizzle i" \
        " saw beyonces tizzles and my pizzle went crizzle, " \
        "mattis we gonna chung, eleifend vitae, nunc. "
COUNT_PLACES = 10
COUNT_ORGANIZATIONS = 5
COUNT_FACILITIES = 13 * COUNT_ORGANIZATIONS
COUNT_NEWSENTRIES = int(COUNT_FACILITIES * 1.5)
COUNT_USERS = 50


def gen_date(hour, day):
    date_today = datetime.date.today() + datetime.timedelta(days=day)
    date_time = datetime.time(hour=hour, minute=0, second=0, microsecond=0)
    new_date = datetime.datetime.combine(date_today, date_time)
    return new_date


def random_string(length=10):
    return u''.join(
        random.choice(string.ascii_letters) for x in range(length))


class Command(BaseCommand):
    help = 'this command creates dummy data for the entire ' \
           'application execute \"python manage.py create_dummy_data 30 --flush True\"' \
           'to first delete all data in the database and then ad random shifts for 30 days.' \
           'if you don\'t want to delete data just not add \"flush True\"   '

    args = ""

    option_list = BaseCommand.option_list

    def add_arguments(self, parser):
        parser.add_argument('days', type=int)
        parser.add_argument('--flush', action='store_true')

    @factory.django.mute_signals(signals.pre_delete)
    def handle(self, *args, **options):
        verbosity = options['verbosity']
        if options['flush']:
            self.print_debug(verbosity, 0, "delete all data in app tables")
            start = time.clock()

            # delete all work related information
            Shift.objects.all().delete()
            Task.objects.all().delete()
            Workplace.objects.all().delete()
            Facility.objects.all().delete()
            Organization.objects.all().delete()

            # delete user accounts (not to be mixed with logins)
            UserAccount.objects.all().delete()
            RegistrationProfile.objects.all().delete()

            # delete geographic information
            Country.objects.all().delete()
            Region.objects.all().delete()
            Area.objects.all().delete()
            Place.objects.all().delete()

            # delete user logins, except super user(s)
            User.objects.filter().exclude(is_superuser=True).delete()

            stop = time.clock()
            self.print_debug(verbosity, 2, "Deletion took {} s", (stop - start))

            # create regional data
            PlaceFactory.create_batch(COUNT_PLACES)
            places = factory.Iterator(Place.objects.all())
            self.print_debug(verbosity, 1, "Created {} places", COUNT_PLACES)

            OrganizationFactory.create_batch(COUNT_ORGANIZATIONS)
            organizations = factory.Iterator(Organization.objects.all())
            self.print_debug(verbosity, 1, "Created {} organizations", COUNT_ORGANIZATIONS)

            FacilityFactory.create_batch(
                COUNT_FACILITIES,
                description=LOREM,
                place=places,
                organization=organizations,
            )
            self.print_debug(verbosity, 1, "Created {} facilities", COUNT_FACILITIES)
            facilities = factory.Iterator(Facility.objects.all())

            TaskFactory.create_batch(COUNT_FACILITIES, facility=facilities)
            self.print_debug(verbosity, 1, "Created {} tasks", COUNT_FACILITIES)

            NewsEntryFactory.create_batch(COUNT_NEWSENTRIES, facility=facilities)
            self.print_debug(verbosity, 1, "Created {} news entries", COUNT_NEWSENTRIES)

            UserAccountFactory.create_batch(COUNT_USERS)
            self.print_debug(verbosity, 1, "Created {} user accounts", COUNT_USERS)

        users = factory.Iterator(UserAccount.objects.all())

        start = time.clock()
        shifts_count = 0
        for facility in Facility.objects.all():
            if 0 != random.randint(1, 100) % 6:
                # pick only random facilities
                # used to fill database with data that are unused but might influence queries
                continue
            tasks = factory.Iterator(Task.objects.filter(facility=facility))
            # generate shifts for number of days
            for day in range(0, options['days']):
                # generate random number of shifts per day and facility
                for i in range(0, random.randint(1, 7)):
                    ending_hour = random.randint(2, 23)
                    shift = ShiftFactory.create(
                        starting_time=gen_date(hour=ending_hour - 1, day=day),
                        ending_time=gen_date(hour=ending_hour, day=day),
                        facility=facility,
                        task=tasks
                    )
                    shifts_count += 1
                    ShiftHelperFactory.create_batch(random.randint(1, 10), user_account=users, shift=shift)

        stop = time.clock()
        self.print_debug(verbosity, 1, "Created {} shifts", shifts_count)
        self.print_debug(verbosity, 2, "Shift creation took {} s", (stop - start))

        self.print_debug(verbosity, 0, "Dummy data created")

    def print_debug(self, verbosity, level, message, *args):
        if level <= verbosity:
            print(message.format(*args))
        pass
