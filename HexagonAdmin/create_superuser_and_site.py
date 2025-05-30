import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HexagonAdmin.settings')
django.setup()


from user.models import User
from django.contrib.sites.models import Site
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def create_superuser():
    username = os.getenv('SUPER_USERNAME')
    email = os.getenv('SUPER_EMAIL')
    password = os.getenv('SUPER_PASSWORD')

    if not User.objects.filter(email=email).exists():
        print(f"Creating account for: {email}")
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='Hexagon',
            last_name='Admin'
        )
        logger.info(f"Superuser created successfully: {email}")
    else:
        logger.info(f"Superuser {email} already exists, skipping creation.")


def setup_site():
    site_name = os.getenv('ADMIN_SITE_NAME', 'Hexagon Education')
    domain = os.getenv('SITE_DOMAIN', 'https://hexagon.edu.vn')

    try:
        site = Site.objects.get(pk=1)
        site.domain = domain
        site.name = site_name
        site.save()
        logger.info(f"{site_name} ({domain})")
    except Site.DoesNotExist:
        Site.objects.create(
            pk=1,
            domain=domain,
            name=site_name
        )
        logger.info(f"Site created: {site_name} ({domain})")


if __name__ == '__main__':
    print("Hexagon Admin is initializing...")
    create_superuser()
    setup_site()
    print("Initialization successfully!")