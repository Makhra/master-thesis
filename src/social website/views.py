from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from stamps.models import Stamp, Collection, ImQuery, ImList, UserProfil, StampInCatalog, ContactRelationship, Interest, Transaction, Message
from stamps.forms import SignupForm, LoginForm, StampForm, CollectionForm, StampInCatalogForm, EditForm, TransactionForm, RegistrationForm, MessageForm
from django.views.generic.simple import direct_to_template
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import F
from myphilately.settings import MEDIA_ROOT

from itertools import chain
import bow
import trainer

def display(request):
    s = get_object_or_404(Stamp, pk=request.GET['stamp'])
    if not request.user.is_authenticated():
        user_profile = None        
        form = None
    else:
        user_profile = request.user.get_profile()
        if request.method =='POST':
            form = CollectionForm(request.POST)
            if form.is_valid():
                try:
                    c = Collection.objects.get(user=user_profile, stamp=s)
                    c.used_quantity=form.cleaned_data['used_quantity']
                    c.unused_quantity=form.cleaned_data['unused_quantity']
                    c.deleted=False
                except Collection.DoesNotExist:
                    c = Collection(user=user_profile, stamp=s, used_quantity=form.cleaned_data['used_quantity'], unused_quantity=form.cleaned_data['unused_quantity'])
                c.save()
                return HttpResponseRedirect('/stamps/collection/')
        else:
            try:
                c = Collection.objects.get(user=user_profile, stamp=s)
                form = CollectionForm(initial={'used_quantity':c.used_quantity, 'unused_quantity':c.unused_quantity})
            except:
                form = CollectionForm(initial={'used_quantity':0, 'unused_quantity':0})
    i = StampInCatalog.objects.filter(stamp_id__exact=s)[:5]
    return render_to_response('stamps/display.html', {'stamp_id' : s, 'catalogs' : i, 'form' : form, 'u' : request.user}, context_instance=RequestContext(request))

@login_required
def upload(request):
    user_profile = request.user.get_profile()
    if request.method == 'POST':
        nb = int(request.POST['nb_cat'])
        try:
            request.POST['add_catalog']            
            addcat = True
            nb = nb + 1
        except:
            try:
                request.POST['del_catalog']
                nb = nb - 1
            except:
                addcat = False
        stampform = StampForm(request.POST, request.FILES, prefix='stampform')
        catalogs = []
        for i in range(0,nb):
            pref = 'catform' + str(i+1)
            j = StampInCatalogForm(request.POST, prefix=pref)
            catalogs.append(j)
        if stampform.is_valid() and addcat == False:
            new_stamp = stampform.save()
            for catform in catalogs:
                if catform.is_valid():
                    c = StampInCatalog(stamp=new_stamp, stampcat_id=catform.cleaned_data['stampcat_id'], catalog_name=catform.cleaned_data['catalog_name'])
                    c.save()
            proc = bow.ProcessImg()
            desc = proc.get_descriptors('%s/%s' % (MEDIA_ROOT, new_stamp.picture))
            matches = proc.add_to_index(desc, new_stamp.id)
            return HttpResponseRedirect('/stamps/display/?stamp=' + str(new_stamp.id))
        else:
            catform = StampInCatalogForm(request.POST, prefix='catform')
    else:
        nb = 1
        stampform = StampForm(prefix='stampform')
    catalogs = [] 
    for i in range(0,nb):
        pref = 'catform' +str(i +1)
        j = StampInCatalogForm(prefix=pref)
        catalogs.append(j)
    extra_context = {
        'stampform' : stampform,
        'catalogs' : catalogs,
        'u' : request.user,
        'nb' : nb,
    }
    return direct_to_template(request, 'stamps/stamp_upload.html', extra_context)

def signup(request):
    if request.user.is_authenticated():
        return HttpRequestRedirect('/stamps/home/')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data['username'], email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            user.save()
            userprofile = user.get_profile()
            userprofile.avatar = form.cleaned_data['avatar']
            userprofile.location = form.cleaned_data['location']
            userprofile.save()
            return HttpResponseRedirect('/stamps/login/')
    else:
        form = RegistrationForm()
    context={
    'form' : form,
    'u' : request.user,
    'title' : 'User Registration',
    }
    return render_to_response('users/auth.html', context, context_instance=RequestContext(request))

def user_login(request):
    if request.user.is_authenticated():
        return HttpRequestRedirect('/stamps/home/')
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect("/stamps/home/")
    form = LoginForm()
    return render_to_response('users/auth.html', {'form' : form, 'u' : request.user, 'title' : 'User authentication'}, context_instance=RequestContext(request))

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/stamps/login/")

@login_required    
def user_edit(request):
    user = request.user
    user_profile = request.user.get_profile()
    if request.method == 'POST':
        eu = EditForm(request.POST, request.FILES, prefix='user')
        if eu.is_valid():
            if eu.cleaned_data['email'] != None:
                user.email = eu.cleaned_data['email']
            if eu.cleaned_data['location'] != None:            
                user_profile.location = eu.cleaned_data['location']
            if eu.cleaned_data['avatar'] != None:
                user_profile.avatar = eu.cleaned_data['avatar']
            user.set_password(eu.cleaned_data['password'])
            user.save()
            user_profile.save()
    else:
        eu = EditForm(initial={'location':user_profile.location, 'email':user.email}, prefix='user')
    return render_to_response('users/edit.html', {'u' : request.user, 'form' : eu}, context_instance=RequestContext(request))
    
    
@login_required    
def user_friends(request):
    friend_result = users_lookup(request, 2)
    user_profile = request.user.get_profile()
    stamps_list = Collection.objects.order_by('-modification_date').filter(user__exact=request.user)#[:5]
    user_interest = get_interest('user', user_profile, 'PE')
    other_interest = get_interest('other', user_profile, 'PE')
    friends = ContactRelationship.objects.order_by('-date').filter(friend=user_profile, type='AC')
    shared = ContactRelationship.objects.order_by('-date').filter(user=user_profile, type='AC')    
    return render_to_response('users/settings.html', {'user' : user_profile, 'f' : friend_result, 'u' : request.user, 'friends' : friends, 'shared' : shared, 'ointerest' : other_interest, 'uinterest' : user_interest}, context_instance=RequestContext(request))

def users_lookup(request, type):
    #related to the user search engine
    if request.method == 'POST':
        friend_name = request.POST['friend_name']
        if type ==1:
            try:
                friend_result = User.objects.filter(username__icontains=friend_name)
            except:
                friend_result = None
        elif type ==2:
            try:
                friend_result = ContactRelationship.objects.filter(user=request.user.get_profile(), friend__user__username__icontains=friend_name)
            except:
                friend_result = None
    else:
        friend_result = None
    return friend_result

@login_required    
def user_home(request):
    friend_result = users_lookup(request, 1)
    user_profile = request.user.get_profile()
    stamps_list = Collection.objects.order_by('-modification_date').filter(user__exact=request.user)[:10]
    pending_request = ContactRelationship.objects.filter(user__exact=user_profile, type__exact='PE')[:10]
    user_interest = Interest.objects.order_by('-date_creation').filter(interested_user__exact=user_profile, state__exact='PE')[:10]
    other_interest = Interest.objects.order_by('-date_creation').filter(collection__user__exact=user_profile, state='PE')[:10]
    return render_to_response('users/home.html', {'user' : user_profile, 'uinterest' : user_interest, 'ointerest' : other_interest, 'pending' : pending_request, 'stamps_list' : stamps_list, 'friend_result' : friend_result, 'u' : request.user}, context_instance=RequestContext(request))

@login_required    
def user_page(request):
    friend_profile = get_object_or_404(UserProfil, pk=request.GET['user'])
    user_profile = request.user.get_profile()
    if friend_profile == user_profile:
        return HttpResponseRedirect('/stamps/home/')
    friend_result = users_lookup(request, 1)
    fu = is_allowed(friend_profile, user_profile)
    uf = is_allowed(user_profile, friend_profile)
    if fu == True:
        stamps_list = Collection.objects.order_by('-modification_date').filter(user__exact=friend_profile)[:5]
        reviewed = get_transaction(friend_profile, 'RE')
    else:
        stamps_list = None
        reviewed = None
    return render_to_response('users/user.html', {'u' : request.user, 'reviewed' : reviewed, 'stamps_list' : stamps_list, 'friend_result' : friend_result, 'user' : friend_profile, 'fu' : fu, 'uf' : uf}, context_instance=RequestContext(request))

def is_allowed(user_profile, friend_profile):
    #check if an user as shared his information to another user
    if user_profile == friend_profile:
        g = True
    else:
        try:
            f = ContactRelationship.objects.get(user__exact=user_profile, friend__exact=friend_profile, type='AC')
            g = True
        except ContactRelationship.DoesNotExist:
            g = False
    return g

@login_required    
def user_collection(request):
    try:
        page_id = int(request.GET['page'])
    except:
        page_id = 1    
    user_profile = request.user.get_profile()
    try:
        friend_profile = get_object_or_404(UserProfil, pk=request.GET['id'])
    except:
        friend_profile = user_profile
    fu = is_allowed(friend_profile, user_profile)
    if fu == False:
        return HttpResponseRedirect("/stamps/collection/")
    stamps_list = Collection.objects.order_by('-modification_date').filter(user__exact=friend_profile, deleted=False)[((page_id - 1)*25):(page_id * 25)]
    counter = len(stamps_list)
    catalogs = []
    interests = Interest.objects.filter(interested_user=user_profile, state='PE')
    user_collection = []
    for interest in interests:
        user_collection.append(interest.collection)
    is_pending = []
    for stamp in stamps_list:
        i = StampInCatalog.objects.filter(stamp=stamp.stamp)
        if not stamp in user_collection:
            j = False
        else:
            j= True
        is_pending.append(j)
        catalogs.append(i)
    return render_to_response('users/collection.html', {'u' : request.user, 'c' : counter, 'p' : page_id, 'user' : friend_profile, 'interests': interests, 'stamps_list' : zip(stamps_list, catalogs, is_pending)}, context_instance=RequestContext(request))

@login_required    
def transaction_review(request):
    transaction = get_object_or_404(Transaction, pk=request.GET['id'])
    user_profile = request.user.get_profile()
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            if transaction.interest.interested_user == user_profile:
                transaction.grade_sender=form.cleaned_data['grade_receiver']
                transaction.review_sender=form.cleaned_data['review_receiver']
                edit_user = transaction.interest.collection.user
                edit_user.grade = (F('grade')*F('transactions_amount') + transaction.grade_sender)/(F('transactions_amount')+1)
                edit_user.transactions_amount = F('transactions_amount') + 1
                edit_user.save()
                if transaction.grade_receiver != None:
                    i = Interest.objects.get(pk=transaction.interest_id)
                    i.state='RE'
                    i.save()
            elif transaction.interest.collection.user == user_profile:
                transaction.grade_receiver=form.cleaned_data['grade_receiver']
                transaction.review_receiver=form.cleaned_data['review_receiver']
                edit_user = transaction.interest.interested_user
                edit_user.grade = (F('grade') + transaction.grade_receiver)/(F('transactions_amount')+1)
                edit_user.transactions_amount = F('transactions_amount') + 1
                edit_user.save()
                if transaction.grade_sender != None:
                    i = Interest.objects.get(pk=transaction.interest_id)
                    i.state='RE'
                    i.save()
            else:
                return HttpResponseRedirect("/stamps/interest/")
            transaction.save()            
            return HttpResponseRedirect("/stamps/interest/")
            
    else:
        if transaction.interest.interested_user == user_profile or transaction.interest.collection.user == user_profile:
            form = TransactionForm()
        else:
            return HttpResponseRedirect("/stamps/interest/")
    return render_to_response('users/transaction_review.html', {'u' : request.user, 'form' : form, 't' : transaction.interest}, context_instance=RequestContext(request))

@login_required    
def transaction_display(request):
    transaction = get_object_or_404(Transaction, pk=request.GET['id'])
    user_profile = request.user.get_profile()
    if is_allowed(transaction.interest.interested_user, user_profile) == True:
        f = transaction.interest.interested_user
    elif is_allowed(transaction.interest.collection.user, user_profile) == True:
        f = transaction.interest.collection.user
    #if transaction.interest.interested_user != user_profile and transaction.interest.collection.user != user_profile:
    else:
        return HttpResponseRedirect("/stamps/interest/")
    stamp = Stamp.objects.get(pk=transaction.interest.collection.stamp.id)
    i = StampInCatalog.objects.filter(stamp_id__exact=stamp)[:5]
    return render_to_response('users/transaction_display.html', {'u' : request.user, 'catalogs' : i, 'stamp_id':stamp, 'f' : f,  't' : transaction}, context_instance=RequestContext(request))

@login_required    
def trade_interest(request):
    try:
        page_id = int(request.GET['page'])
    except:
        page_id = 1    
    user_profile = request.user.get_profile()
    user_interest = get_interest('user', user_profile, 'PE')[:15]
    user_accepted = get_interest('user', user_profile, 'AC')[:15]
    other_interest = get_interest('other', user_profile, 'PE')[:15]
    other_accepted = get_interest('other', user_profile, 'AC')[:15]
    user_accepted = sorted(chain(user_accepted, other_accepted), key=lambda instance: instance.date_creation, reverse=True)[:15]
    to_review = get_transaction(user_profile, 'DO')[:15]
    reviewed = get_transaction(user_profile, 'RE')[:15]
    reviewed = reviewed[((page_id - 1)*25):(page_id * 25)]
    counter = len(reviewed)
    return render_to_response('users/interests.html', {'u' : request.user,  'c' : counter, 'p' : page_id, 'reviewed' : reviewed, 'to_review': to_review, 'uacc' : user_accepted, 'uinterest':user_interest, 'ointerest':other_interest}, context_instance=RequestContext(request))

def get_transaction(user_profile, state):
    u = Transaction.objects.filter(interest__interested_user=user_profile, interest__state=state)
    o = Transaction.objects.filter(interest__collection__user=user_profile, interest__state__exact=state)
    u = sorted(chain(u, o), key=lambda instance: instance.interest.date_creation, reverse=True)
    return u

def get_interest(type, user_profile, state):
    if type == 'user':
        interest = Interest.objects.order_by('-date_creation').filter(interested_user__exact=user_profile, state__exact=state)[:25]
    elif type == 'other':
        interest = Interest.objects.order_by('-date_creation').filter(collection__user__exact=user_profile, state=state)[:25]   
    else:
        interest = None
    return interest

def interest_manager(request, state):
    interest_stamp = get_object_or_404(Interest, pk=request.GET['id'])
    user_profile = request.user.get_profile()
    if interest_stamp.collection.user == user_profile or (interested_stamp.interested_user == user_profile and state == 'AC'):
        try:
            c = Interest.objects.get(pk=interest_stamp.id)
            if state == 'DE':
                c.delete()
            else:
                c.state=state
                c.save()
        except Interest.DoesNotExist:
            c = None
    else:
        c = None
    return c

@login_required    
def interested(request):
    interest_stamp = get_object_or_404(Collection, pk=request.GET['id'])
    user_profile = request.user.get_profile()
    try:
        c = Interest.objects.get(collection=interest_stamp, interested_user=user_profile)
    except Interest.DoesNotExist:
        c = Interest(collection=interest_stamp, interested_user=user_profile)
        c.save()
    return HttpResponseRedirect('/stamps/collection/?id=' + str(interest_stamp.user_id))

@login_required    
def interest_confirmed(request):
    interest = interest_manager(request, 'AC')
    return HttpResponseRedirect('/stamps/interest/')

@login_required    
def interest_canceled(request):
    interest_manager(request, 'DE')
    return HttpResponseRedirect('/stamps/interest/')

@login_required    
def transaction_confirmed(request):
    confirmed_interest = interest_manager(request, 'DO')
    transaction = Transaction(interest=confirmed_interest)
    transaction.save()
    return HttpResponseRedirect('/stamps/transaction_review/?id=' + str(transaction.interest_id))
    
@login_required
def transaction_canceled(request):
    interest_manager(request, 'DE')
    return HttpResponseRedirect('/stamps/interest/')

@login_required
def request_confirmed(request):
    friend_profile = get_object_or_404(UserProfil, pk=request.GET['user'])
    user_profile = request.user.get_profile()

    try:
        c = ContactRelationship.objects.get(user=user_profile, friend=friend_profile, type="PE")
        c.type="AC"
    except ContactRelationship.DoesNotExist:
        c = ContactRelationship(user=user_profile, friend=friend_profile, type="AC")
    c.save()
    try:
        d = ContactRelationship.objects.get(user=friend_profile, friend=user_profile)
    except ContactRelationship.DoesNotExist:
        d = ContactRelationship(user=friend_profile, friend=user_profile, type="PE")
        d.save()
    return HttpResponseRedirect('/stamps/user/?user='+ str(friend_profile.user_id))

@login_required
def request_canceled(request):
    friend_profile = get_object_or_404(UserProfil, pk=request.GET['user'])
    user_profile = request.user.get_profile()
    try:
        c = ContactRelationship.objects.get(user=user_profile, friend=friend_profile)
        c.delete()
    except:
        c = None
    return HttpResponseRedirect('/stamps/home')
    
def stamps_list(request):
    try:
        page_id = int(request.GET['page'])
    except:
        page_id = 1
    if request.method == 'POST':
        if request.POST.get('updatesearch'):
            page_id = 1
            search = request.POST['search']
            criteria = request.POST['criteria']
            stamps_list = generate_request(search, criteria, page_id)
        else:
            HttpResponseRedirect('/stamps/stamps')
    else:
        try:
            search = request.POST['hsearch']
            criteria = request.POST['hcriteria']
        except:
            search = None
            criteria = None
        stamps_list = Stamp.objects.order_by('-id')[((page_id - 1)*25):(page_id * 25)]
    counter = stamps_list.count()
    catalogs = []
    for stamp in stamps_list:
        try:
            i = StampInCatalog.objects.filter(stamp_id=stamp.id)
        except StampInCatalog.DoesNotExist:
            i = None
        catalogs.append(i)
    return render_to_response('stamps/list.html', {'c': counter, 'p': page_id, 'sear' : search, 'crit' : criteria, 'u' : request.user, 'stamps_list' : zip(stamps_list, catalogs)}, context_instance=RequestContext(request))

def generate_request(search, criteria, page_id):
    if criteria == 'issue_country':
        stamps_list = Stamp.objects.order_by('-id').filter(issue_country__icontains=search)[((page_id - 1)*25):(page_id * 25)]
    elif criteria =='issue_year':
        stamps_list = Stamp.objects.order_by('-id').filter(issue_year__icontains=search)[((page_id - 1)*25):(page_id * 25)]
    elif criteria == 'color':
        stamps_list = Stamp.objects.order_by('-id').filter(color__icontains=search)[((page_id - 1)*25):(page_id * 25)]
    else:
        stamps_list = None
    return stamps_list


def all_messages(request):
    user_profile = request.user.get_profile()
    try:
        r = Message.objects.order_by('sender', '-id').distinct('sender').filter(receiver=user_profile)
    except:
        r = None
    return render_to_response('users/mailbox.html', {'u' : request.user, 'messages' : r}, context_instance=RequestContext(request))


@login_required
def get_messages(request):
    friend_profile = get_object_or_404(UserProfil, pk=request.GET['user'])
    user_profile = request.user.get_profile()
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            m = Message(sender=user_profile, receiver=friend_profile, message=form.cleaned_data['message'])
            m.save()
    try:
        s = Message.objects.filter(sender=user_profile, receiver=friend_profile)
    except:
        s = None
    try:
        r = Message.objects.filter(sender=friend_profile, receiver=user_profile)
    except:
        r = None
    messages_flow = sorted(chain(s, r), key=lambda instance: instance.sent_time)
    for mes in r:
        if mes.seen == False:
            mes.seen = True
            mes.save()
    form = MessageForm()
    return render_to_response('users/messages.html', {'u' : request.user, 'form' : form, 'messages' : messages_flow}, context_instance=RequestContext(request))

@login_required
def delete_collection(request):
    dcollection = get_object_or_404(Collection, pk=request.GET['id'])
    user_profile = request.user.get_profile()
    if dcollection.user == user_profile:
        try:
            i = Interest.objects.get(collection=dcollection)
        except:
            i = None
        if i == None:
            dcollection.delete()
        else:
            dcollection.deleted = True
            dcollection.save()
    return HttpResponseRedirect('/stamps/collection/')

def match_finder(request):
    if request.method == 'POST':
        if 's_pic' in request.FILES:
            pic = request.FILES['s_pic']
            im = ImQuery()
            im.up_stamp.save(pic.name, pic)
            proc = bow.ProcessImg()
            desc = proc.get_descriptors('%s/temp/%s' % (MEDIA_ROOT, pic.name))
            matches = proc.query_db(desc)
            items = []
            for mat in matches:
                ima = Stamp.objects.get(pk=mat[1])
                items.append(ima)

        else:
            matches = []
            items = []
            im=[]
    else:
        matches = []
        items = []
        im = []
    return render_to_response('stamps/finder.html', {'desc' : items, 'q' : im, 'u' : request.user}, context_instance=RequestContext(request))