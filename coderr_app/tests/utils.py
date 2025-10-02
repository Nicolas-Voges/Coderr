from django.utils import timezone

from auth_app.tests.utils import create_test_image_file
from coderr_app.models import Offer, Detail

min_time = 5
min_price = 50

def create_offer(user):
        """
        Helper method to create an Offer with default test data.
        """
        return Offer.objects.create(
            user=user,
            title='Testtitle',
            image=create_test_image_file(),
            description="Test",
            created_at=timezone.now()
        )

def create_detail(offer_id, time=5, price=100, offer_type='basic'):
    return Detail.objects.create(
            title=offer_type + " Design",
            revisions=10,
            delivery_time_in_days=time,
            price=price,
            features=[
                        "Logo Design",
                        "Visitenkarte",
                        "Briefpapier",
                        "Flyer"
                ],
            offer_type=offer_type,
            offer_id=offer_id
        )


def create_detail_set(offer_id):
    return (
        create_detail(
            offer_id=offer_id,
            time=min_time,
            price=min_price
        ),
        create_detail(
            offer_id=offer_id,
            time=15,
            price=999,
            offer_type='standard'
        ),
        create_detail(
            offer_id=offer_id,
            time=15,
            price=999,
            offer_type='premium'
        )
    )