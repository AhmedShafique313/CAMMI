import stripe, os
from dotenv import load_dotenv
load_dotenv(dotenv_path=r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\.env")
stripe.api_key = os.getenv("STRIPE_API_KEY")

starter_subscription = stripe.Product.create(
  name="Starter Subscription",
  description="$12/Month subscription",
)

starter_subscription_price = stripe.Price.create(
  unit_amount=12,
  currency="usd",
  recurring={"interval": "month"},
  product=starter_subscription['id'],
)

# Save these identifiers
print(f"Success! Here is your starter subscription product id: {starter_subscription.id}")
print(f"Success! Here is your starter subscription price id: {starter_subscription_price.id}")