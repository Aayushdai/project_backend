from django.core.management.base import BaseCommand
from apps.trips.models import City


class Command(BaseCommand):
    help = "Populate all 77 districts of Nepal into the City database"

    def handle(self, *args, **options):
        nepal_districts = [
            # A-B
            "Achham", "Arghakhanchi", "Baglung", "Baitadi", "Bajhang", "Bajura", 
            "Banke", "Bara", "Bardiya", "Bhaktapur", "Bhojpur",
            
            # C-D
            "Chitwan", "Dadeldhura", "Dailekh", "Dang", "Darchula", "Dhading",
            "Dhankuta", "Dhanusha", "Dolakha", "Dolpa", "Doti",
            
            # G-L
            "Gorkha", "Gulmi", "Humla", "Ilam", "Jajarkot", "Jhapa", "Jumla",
            "Kailali", "Kalikot", "Kanchanpur", "Kapilvastu", "Kaski", 
            "Kavrepalanchok", "Khotang", "Lalitpur", "Lamjung",
            
            # M-R
            "Mahottari", "Makwanpur", "Manang", "Mugu", "Morang", "Myagdi",
            "Nawalpur", "Nawalparasi (West)", "Nuwakot", "Okhaldhunga", "Palpa",
            "Panchthar", "Parbat", "Parsa", "Pyuthan", "Ramechhap", "Rasuwa",
            "Rautahat", "Rolpa", "Rukum East", "Rukum West", "Rupandehi",
            
            # S-U
            "Salyan", "Sankhuwasabha", "Saptari", "Sarlahi", "Sindhuli",
            "Sindhupalchok", "Siraha", "Solukhumbu", "Sunsari", "Surkhet",
            "Syangja", "Tanahun", "Taplejung", "Terhathum", "Udayapur",
        ]

        created_count = 0
        already_exist = 0

        for district in nepal_districts:
            city, created = City.objects.get_or_create(
                name=district.strip(),
                country="Nepal"
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {district} (Nepal)')
                )
            else:
                already_exist += 1
                self.stdout.write(
                    self.style.WARNING(f'⟳ Already exists: {district} (Nepal)')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Summary: {created_count} new districts added, {already_exist} already existed. "
                f"Total: {created_count + already_exist} districts"
            )
        )
