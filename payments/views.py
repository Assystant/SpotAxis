from __future__ import absolute_import
from __future__ import print_function
from django.conf import settings
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from payments.models import *
from companies.models import *
from datetime import datetime, timedelta
import paypalrestsdk
import json
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from utils import validate_code
"""# Create your views here.
# gateway = braintree.BraintreeGateway(access_token=settings.BRAINTREE_ACCESS_TOKEN)
# gateway = braintree.Configuration.gateway()"""

"""
This module handles the payment processing view for company subscription plans.

It provides logic for:
- Calculating prorated charges based on plan change and remaining subscription period.
- Validating discount codes and applying discounts or account credits.
- Adjusting company wallet balances and recording all transaction events.
- Managing scheduled transactions and updating subscription details such as plan and user count.

Dependencies include Django's authentication and messaging frameworks, PayPal SDK, and internal utility and model references.
"""

@login_required
@csrf_exempt
def payment(request):
    """
    Handles the company’s subscription and payment processing.

    This function enables an admin recruiter to:
    - Change or renew a subscription plan.
    - Add additional users to a subscription.
    - Validate and apply discount codes.
    - Redeem unused subscription days as wallet credit.
    - Deduct payment amounts from the company wallet.
    - Record all transactions including credits and debits.

    Parameters:
        request (HttpRequest): The incoming HTTP request object from the user.

    Returns:
        HttpResponse: Rendered HTML response with appropriate success or error messages.

    Raises:
        Http404: If any essential model or data is not found or invalid access is attempted.
        ValueError: For validation or unexpected computation issues (during development/debugging).
    """
    # raise ValueError()
    if request.user.profile.codename == 'recruiter' and request.user.recruiter.is_admin():
        payment_min = 10
        original_amount_to_pay = 0.00
        amount_to_pay = 0.00
        slab = None
        company = request.user.recruiter.company.all()[0]
        wallet = company.wallet
        subscription = company.subscription
        current_slab = company.subscription.price_slab
        client_token = None
        # client_token = gateway.client_token.generate({
                # 'customer_id': company.id,
            # })
        hasSufficientCredit = False
        remove_users = False
        compulsary_remove = False
        renewal = 0.00
        add_to_account = 0.00
        if request.POST:
            plan = request.POST.get('plan',0)
            if plan:
                slab = PriceSlab.objects.get(id = plan)
            else:
                slab = current_slab
            try:
                future_slab = company.scheduledtransactions_set.all()[0].price_slab
            except:
                future_slab = slab
            code = request.POST.get('code')
            added_users = int(request.POST.get('added_users',0))
            user_count = company.recruiter_set.all().count()
            update_immediately = request.POST.get('update_immediately', False)
            if update_immediately:
                update_immediately = True
            max_users = slab.package.max_users
            free_users = slab.package.free_users
            consolidation_ratio = 1
            if current_slab.expiry_period:
                consolidation_ratio = Decimal((company.subscription.expiry - datetime.now()).days)/Decimal(current_slab.expiry_period)
            if consolidation_ratio < 0:
                consolidation_ratio = 1
            # if update_immediately or not company.subscription.expiry:

            if not max_users == 0 and free_users + added_users > max_users:
                messages.error(request,'You are exceeding the max user limit on this plan, Please recheck and try again')
            else:
                if current_slab != slab:
                    # raise ValueError(validate_code(code, slab, company))
                    if not validate_code(code, slab, company):
                        messages.error(request, 'Invalid Code. Transaction Halted')
                        request.session['slab'] = plan
                    else:
                        refund = 0
                        # amount_to_pay = Decimal(request.POST.get('amount_to_pay',0))
                        if not slab.amount:
                            slab.amount = Decimal(0.00)
                        if not current_slab.amount:
                            current_slab.amount = Decimal(0.00)
                        period = Decimal(current_slab.expiry_period)
                        if not period:
                            period = 1
                        if company.subscription.expiry:
                            days_left = Decimal((company.subscription.expiry - datetime.now()).days)
                        else:
                            days_left = 0
                        carried_forward_balance = (days_left/period)*current_slab.amount
                        redeem = (days_left/period)*current_slab.amount
                        users_redeem = (days_left/period) * current_slab.price_per_user * company.subscription.added_users
                        price_diff = slab.amount - redeem - users_redeem
                        amount_to_pay = price_diff
                        # else:
                        #     if slab.amount:
                        #         amount_to_pay = slab.amount
                        #     else:
                        #         amount_to_pay = 0
                        amount_to_pay = Decimal(amount_to_pay)

                        if code:
                            discount = Discount.objects.get(label__iexact = code)
                            if discount.transaction_type == 'S':
                                if discount.type == 'V':
                                    refund = discount.amount
                                elif discount.type == 'P':
                                    refund = slab.amount* discount.amount / 100
                                
                                # if amount_to_pay < 0:
                                #     amount_to_pay = 0
                                amount_to_pay = amount_to_pay - refund
                                add_to_account = 0
                            elif discount.transaction_type == 'A':
                                refund = 0
                                if discount.type == 'V':
                                    # refund = discount.amount
                                    add_to_account = discount.amount
                                elif discount.type == 'P':
                                    # refund = discount.amount * amount_to_pay / 100
                                    add_to_account = discount.amount * amount_to_pay / 100
                        else:
                            discount = None
                        user_amount_to_pay = added_users * slab.price_per_user
                        amount_to_pay = amount_to_pay + Decimal(user_amount_to_pay)
                        total_redeem = users_redeem + redeem
                        total_to_pay = slab.amount + user_amount_to_pay
                        # if amount_to_pay < 0:
                        #     amount_to_pay = 0
                        # raise ValueError()
                        if company.wallet.available + total_redeem + refund< total_to_pay:
                            messages.error(request, 'Insufficient Credits!')
                        else:
                            subscription.price_slab = slab
                            if slab.expiry_period:
                                subscription.expiry = datetime.now() + timedelta(days=int(slab.expiry_period))
                            else:
                                subscription.expiry = None
                            subscription.added_users = added_users
                            subscription.save()
                            scheduled = ScheduledTransactions.objects.filter(company = company)
                            if scheduled:
                                scheduled.delete()

                            # wallet.available = wallet.available - amount_to_pay + Decimal(add_to_account)
                            if not wallet.currency:
                                wallet.currency = slab.currency
                            # wallet.save()

                            if discount and discount.transaction_type == 'S':
                                if refund < 0:
                                    refund = refund * -1
                                wallet.available = wallet.available + Decimal(refund)
                                # wallet.save()
                                Transactions.objects.create(user = request.user, company = company, type="A", amount = refund, reason = 'Credits added using discount code ' + code, balance = wallet.available)
                            if total_redeem > 0:
                                wallet.available  = wallet.available + total_redeem
                                # wallet.save()
                                Transactions.objects.create(user = request.user, company = company, type="A", amount = total_redeem, reason = 'Carried Forward Balance adjusted with plan' , balance = wallet.available)
                            reason = 'Plan changed to ' + str(slab)
                            if slab.get_slab_period_display():
                                reason = reason + ' ' + str(slab.get_slab_period_display())
                            if added_users:
                                reason = reason + ' with ' + str(added_users) + ' additional users. '
                            wallet.available = wallet.available - total_to_pay
                            Transactions.objects.create(user = request.user, company = company, type="R", amount=total_to_pay, reason = reason, balance = wallet.available)
                            if discount and discount.transaction_type == 'A':
                                wallet.available = wallet.available + add_to_account
                                Transactions.objects.create(user = request.user, company = company, type="A", amount = refund, reason = 'Credits added using discount code ' + code, balance = wallet.available)
                            wallet.save()
                            if discount:
                                usage = discount.discount_usage_set.all().filter(company = company)[0]
                                usage.used_count = usage.used_count + 1
                                usage.save()

                                # raise ValueError(usage.used_count)
                                # print(usage)
                                # print(usage.used_count)
                            messages.success(request, 'Plan Subscription updated')
                        # if slab.amount and current_slab.amount and slab.amount > current_slab.amount:
                        #     period = current_slab.expiry_period
                        #     days_left = (company.subscription.expiry - datetime.now()).days
                        #     price_diff = slab.amount - current_slab.amount
                        #     amount_to_pay = (days_left/period)*price_diff
                        # else:
                        #     amount_to_pay = slab.amount
                else:
                    if added_users == company.subscription.added_users:
                        messages.error(request, 'No change recognised. Please confirm the values and try again!')
                    else:
                        user_amount_to_pay = (added_users-company.subscription.added_users) * slab.price_per_user * consolidation_ratio
                        amount_to_pay = Decimal(user_amount_to_pay)
                        if company.wallet.available < amount_to_pay:
                            messages.error(request, 'Insufficient Credits!')
                        else:
                            subscription.added_users = added_users
                            subscription.save()
                            scheduled = ScheduledTransactions.objects.filter(company = company)
                            if scheduled:
                                scheduled.delete()
                            wallet.available = wallet.available - amount_to_pay
                            if not wallet.currency:
                                wallet.currency = slab.currency
                            wallet.save()
                            reason = 'Additional Users count updated to ' + str(added_users)
                            if amount_to_pay < 0:
                                Transactions.objects.create(user = request.user, company = company, type="A", amount=(amount_to_pay*-1), reason = reason, balance = wallet.available)
                            else:
                                Transactions.objects.create(user = request.user, company = company, type="R", amount=amount_to_pay, reason = reason, balance = wallet.available)
                            messages.success(request, 'Additional Users Updated')

            # else:
            #     if not max_users == 0 and free_users + added_users > max_users:
            #         messages.error(request,'You are exceeding the max user limit on this plan, Please recheck and try again')
            #     else:
            #         if not validate_code(code, slab, company):
            #             messages.error(request, 'Invalid Code. Transaction Halted')
            #             request.session['slab'] = plan
            #         else:

            #             refund = 0
            #             # amount_to_pay = Decimal(request.POST.get('amount_to_pay',0))
            #             if slab.amount and current_slab.amount:
            #                 period = Decimal(current_slab.expiry_period)
            #                 days_left = Decimal((company.subscription.expiry - datetime.now()).days)
            #                 redeem = (days_left/period)*current_slab.amount
            #                 price_diff = slab.amount - redeem
            #                 amount_to_pay = price_diff
            #                 if amount_to_pay < 0:
            #                     amount_to_pay = 0
            #             else:
            #                 if slab.amount:
            #                     amount_to_pay = slab.amount
            #                 else:
            #                     amount_to_pay = 0
            #             amount_to_pay = Decimal(amount_to_pay)
            #             if code:
            #                 discount = Discount.objects.get(label__iexact = code)
            #                 if discount.transaction_type == 'S':
            #                     if discount.type == 'V':
            #                         refund = discount.amount
            #                         amount_to_pay = amount_to_pay - discount.amount
            #                     elif discount.type == 'P':
            #                         refund = amount_to_pay * discount.amount / 100
            #                         amount_to_pay = amount_to_pay *(1- (discount.amount/100))
            #                     if amount_to_pay < 0:
            #                         amount_to_pay = 0
            #                 elif discount.transaction_type == 'A':
            #                     if discount.type == 'V':
            #                         refund = discount.amount
            #                         add_to_account = discount.amount
            #                     elif discount.type == 'P':
            #                         refund = discount.amount * amount_to_pay / 100
            #                         add_to_account = discount.amount * amount_to_pay / 100
            #             else:
            #                 discount = None
            #             if company.wallet.available< amount_to_pay:
            #                 messages.error(request, 'Insufficient Credits!')
            #             else:
            #                 #schedule the transaction
            #                 scheduled, created = ScheduledTransactions.objects.get_or_create(company = company)
            #                 if current_slab == slab:
            #                     #only change users
            #                     scheduled.added_users = added_users
            #                     if not scheduled.price_slab:
            #                         scheduled.price_slab = slab
            #                     scheduled.user = request.user
            #                 else:
            #                     #schedule plan change + user change
            #                     scheduled.user = request.user
            #                     scheduled.discount = discount
            #                     scheduled.added_users = added_users
            #                     scheduled.price_slab = slab
            #                 scheduled.save()
            #                 if discount:
            #                     usage = discount.discount_usage_set.all().filter(company = company)[0]
            #                     usage.used_count = usage.used_count + 1
            #                     usage.save()
            #                 message = 'Your plan will be updated to ' + str(scheduled.price_slab.package) + ' ' + str(scheduled.price_slab.get_slab_period_display())
            #                 if scheduled.added_users:
            #                     message = message + ' with ' + str(scheduled.added_users) + ' additional users'
            #                 if company.subscription.expiry:
            #                     message = message + ' upon expiry of current plan on ' + str(company.subscription.expiry.date())
            #                 messages.success(request, message)

        else:
            messages.error(request, 'Unauthorised Transaction')
    else:
          messages.error(request,'Unauthorised Transaction')
          raise Http404
    return redirect('companies_billing')

@login_required
@csrf_exempt
def checkout(request):
    """
    Handles the PayPal payment checkout process for purchasing credits for a company.

    This view supports both POST and GET requests. On a POST request, it initiates a payment
    using the PayPal SDK by creating a web experience profile and a payment object. If payment
    creation is successful, it redirects the user to the PayPal approval URL. On a GET request,
    it handles PayPal's redirect back to the site, confirms the payment execution, updates the
    wallet balance, logs the transaction, and redirects the user to the billing page.

    Args:
        request (HttpRequest): The HTTP request object containing method, user, POST/GET data.

    Returns:
        HttpResponseRedirect: Redirects the user either to PayPal or back to the billing page
        depending on the payment flow.

    Modules Used:
        - `paypalrestsdk`: Used to interact with PayPal for creating payments and profiles.
        - `settings`: Retrieves site-wide configurations like SITE_URL.
        - `datetime`: Appends timestamps to names to avoid conflicts.
        - `decimal`: Ensures currency values are handled with precision.
        - `messages`: Provides user feedback via Django's messaging framework.
        - `redirect`: Redirects user to a different URL based on payment outcome.

    Payment Flow:
        1. User selects slab and amount.
        2. Payment is created with PayPal.
        3. User is redirected to PayPal.
        4. On approval or cancelation, PayPal redirects back to the site.
        5. Payment is executed and credits are added to the company's wallet.
    """
    # token = paypalrestsdk.get_token()
    # raise ValueError()
    company = request.user.recruiter.company.all()[0]
    slab = request.POST.get('slab')
    amount_to_pay = request.POST.get('amount_to_pay')
    if amount_to_pay:
        img = str(settings.SITE_URL)+ "/static/img/logo/logo_small.png"
        # web_profiles = paypalrestsdk.WebProfile.all()
        # print(web_profiles)
        # if web_profiles.to_dict():
        #     for web_profile in web_profiles:
        #         paypalrestsdk.WebProfile.find(web_profile.id).delete()
        name = "Spot-Axis"+str(request.user.id) + str(datetime.now())
        web_profile = paypalrestsdk.WebProfile({
            "name": 'SpotAxis',
            "presentation": {
                "brand_name": "SpotAxis",
                "logo_image":  img,
                "locale_code": "US"
            },
            'temporary': True,
            "input_fields": {
                "allow_note": True,
                "no_shipping": 1,
                "address_override": 1
            },
            "flow_config": {
                "landing_page_type": "billing",
                "bank_txn_pending_url": settings.SITE_URL,
                "user_action": "commit"
            }
        })
        if not web_profile.create():
            # messages.error(request,web_profile.error)
            print((web_profile.error))
            print(name)
        else:
            print((web_profile.id))
        # return_url = settings.SITE_URL + "/checkout/?success=true&slab="+str(slab)
        return_url = request.scheme+"://"+request.get_host() + "/checkout/?success=true&slab="+str(slab)
        # cancel_url = settings.SITE_URL + "/checkout/?success=true&slab="+str(slab)
        cancel_url = request.scheme+"://" +request.get_host() + "/checkout/?cancel=true&slab="+str(slab)
        payment = paypalrestsdk.Payment({
              "intent": "sale",
              "experience_profile_id": web_profile.id,
              "payer": {
                "payment_method": "paypal" },
              "redirect_urls": {
                "return_url": return_url,
                "cancel_url": cancel_url
              },
              "transactions": [ {
                "amount": {
                  "total": amount_to_pay,
                  "currency": "USD" },
                "description": "Adding Credits to SpotAxis" } ] } )
        if payment.create():
            print(("Payment[%s] created successfully" % (payment.id)))
            # Redirect the user to given approval url
            for link in payment.links:
                if link.method == "REDIRECT":
                    # Convert to str to avoid google appengine unicode issue
                    # https://github.com/paypal/rest-api-sdk-python/pull/58
                    redirect_url = str(link.href) #+ '&useraction=commit'
                    print(("Redirect for approval: %s" % (redirect_url)))
                    return redirect(redirect_url)
        else:
            print("Error while creating payment:")
            print((payment.error))
            messages.error(request,payment.error)
    else:
        try:
            success = request.GET['success']
        except:
            success = False
        try:
            cancel = request.GET['cancel']
        except:
            cancel = False
        if success or cancel:
            slab = request.GET.get('slab')
            request.session['slab'] = slab
        else:
            request.session['slab'] = None
        if success:
            payment = paypalrestsdk.Payment.find(request.GET['paymentId'])
            payment.execute({"payer_id": request.GET['PayerID']}) 
            amount_paid = payment.find(request.GET['paymentId'])['transactions'][0]['amount']['total']
            transaction = Transactions.objects.create(user = request.user, company = company, type="A", amount = amount_paid, reason = "Credits Added")
            if payment['state'] == 'approved':
                try:
                    wallet = company.wallet
                except:
                    wallet = Wallet.objects.create(company = company, available=0)
                wallet.available = wallet.available + Decimal(amount_paid.strip())
                wallet.save()
                transaction.status = True
                messages.success(request,'Credits Added Successfully')
            else:
                transaction.status = False
                messages.error(request,'Fund Transfer not Approved')
            transaction.balance = company.wallet.available
            transaction.save()

            # slab = request.GET['slab']
            # raise ValueError(payment['state'])
            # return HttpResponse()
            # request.session['payment'] = json.dumps(payment)
        elif cancel:
            # raise ValueError()
            # transaction = Transaction.objects.create(user = request.user, company = company, type="A", amount = amount_paid, reason = "Credits Added")
            messages.error(request,'Payment Cancelled.')
            # return render('checkout.html')
    return redirect('/billing/')
