# Copyright (C) 2011  Governo do Estado do Rio Grande do Sul
#
#   Author: Lincoln de Sousa <lincoln@gg.rs.gov.br>
#   Author: Rodrigo Sebastiao da Rosa <rodrigo-rosa@procergs.rs.gov.br>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Module that uses the Template and Model APIs to build the Admin web
interface.
"""
import urllib 
import json


from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import desc, not_
from gd.model import Audience, Buzz, Term, session, AudiencePosts
from gd.utils import msg
from gd import auth, conf
from gd.content.wp import wordpress


admin = Blueprint(
    'admin', __name__,
    template_folder='templates',
    static_folder='static')


@admin.route('/login', methods=('POST', 'GET'))
def login():
    """Renders the login form and calls login machinery"""
    error = None
    if request.method == 'POST':
        reqv = request.values.get
        try:
            auth.login(reqv('username'), reqv('password'))
            nexturl = request.values.get('next')
            if nexturl:
                return redirect(nexturl)
        except auth.AuthError, exc:
            error = exc.__class__.__name__
    return render_template(
        'admin/login.html', title=_(u'Login'), error=error,
        hide_menu=True)


@admin.route('/logout')
def logout():
    """Calls the logout API function and redirects to the login form"""
    auth.logout()
    return redirect(url_for('.login'))


@admin.route('/')
@auth.checkroles(['administrator'])
def index():
    return redirect('/admin/audience')

@admin.route('/audience')
@auth.checkroles(['administrator'])
def audiences():
    """Main view, lists all registered audiencces"""
    pagination, inst = wordpress.wpgove.getAudiencias(allaudiencia='T')
    return render_template('admin/listing.html', title=_(u'Audience'),
                            audiences=inst,
                            pagination=pagination,)


@admin.route('/audience/<int:aid>/status/<status>')
@auth.checkroles(['administrator'])
def audience_status(aid, status):
    """Changes the status of an audience"""
    active = Audience.query.filter_by(started=True).first()
    if active:
        active.started = False
    inst = Audience.query.get(aid)
    inst.started = status == 'true'
    if status == 'true':
        inst.date_started = datetime.now()
    session.commit()
    return redirect(url_for('.audiences'))


@admin.route('/audience/new', methods=('GET', 'POST'))
@auth.checkroles(['administrator'])
def new():
    """Shows the form that creates new audiences and save collected data
    in the database.
    """
    if request.method == 'POST':
        inst = Audience()
        inst.title = request.form['title']
        inst.subject = request.form['subject']
        inst.date = datetime.strptime(request.form['date'], conf.DATEFORMAT)
        inst.description = request.form['description']
        inst.embed = request.form['embed']
        inst.visible = request.form['visible']
        terms = request.form.getlist('term')
        main = request.form['main']
        for term in terms:
            newterm = Term(hashtag=term, main=(main==term))
            inst.terms.append(newterm)

        inst.owner = 'administrator'
        session.commit()
        return redirect(url_for('.audiences'))
    return render_template('admin/new.html', title=_(u'Audience'))


@admin.route('/audience/<int:aid>', methods=('GET', 'POST'))
@auth.checkroles(['administrator'])
def edit(aid):
    """Returns a form to edit an audience and saves new params in the
    database.
    """
    inst = Audience.query.get(aid)
    if request.method == 'POST':
        inst.title = request.form['title']
        inst.subject = request.form['subject']
        inst.date = datetime.strptime(request.form['date'], conf.DATEFORMAT)
        inst.description = request.form['description']
        inst.embed = request.form['embed']
        inst.visible = request.form['visible']

        # deleting all terms
        term = Term.query.filter_by(audience=inst)
        term.delete()

        # adding new terms defined by the user
        terms = request.form.getlist('term')
        main = request.form['main']
        for term in terms:
            newterm = Term(hashtag=term, main=(main==term))
            inst.terms.append(newterm)

        # temporary owner for all objects created in the admin
        # interface.
        inst.owner = 'administrator'

        session.commit()
        return redirect(url_for('.audiences'))

    return render_template(
        'admin/edit.html', title=_(u'Audience'), inst=inst)


@admin.route('/audience/<int:aid>/delete', methods=['GET', 'POST'])
@auth.checkroles(['administrator'])
def remove(aid):
    """Delete an audience instance and its related terms in the
    database."""
    audience = Audience.query.get(aid)
    term = Term.query.filter_by(audience=audience)
    term.delete()
    audience.delete()
    session.commit()
    return redirect(url_for('.audiences'))


@admin.route('/audience/<int:aid>/moderate')
@auth.checkroles(['administrator'])
def moderate(aid):
    """Returns a list of buzzes for moderation."""
    audience = AudiencePosts.query.get(aid)
    print aid
    status = Buzz.status.in_([u'inserted']) \
        if request.values.get('status', 'new') == 'new' \
        else not_(Buzz.status.in_([u'inserted']))
    buzz_list = Buzz.query \
        .filter_by(audience_id=audience) \
        .filter(status) \
        .order_by(desc('creation_date'))
        
    return render_template(
        'admin/moderate.html', audience=audience, buzz_list=buzz_list,
        title=_(u'Audience'))


@admin.route('/audience/<int:aid>/publish')
@auth.checkroles(['administrator'])
def publish(aid):
    """Returns a list of buzzes for publication."""
    audience = Audience.query.get(aid)
    status = Buzz.status.in_([u'selected']) \
        if request.values.get('status', 'new') == 'new' \
        else Buzz.status.in_([u'published'])
    buzz_list = Buzz.query \
        .filter_by(audience=audience) \
        .filter(status) \
        .order_by(desc('creation_date'))
    return render_template(
        'admin/publish.html', audience=audience, buzz_list=buzz_list)


@admin.route('/audience/batch', methods=('post',))
@auth.checkroles(['administrator'])
def batch():
    """Batch processing a list of buzz notices"""
    action = request.form['action']
    notices = Buzz.query.filter(Buzz.id.in_(request.form.getlist('notice')))
    { 'accept': lambda: [setattr(i, 'status', u'approved') for i in notices],
      'remove': lambda: [i.delete() for i in notices],
      'suggest': lambda: [setattr(i, 'status', u'selected') for i in notices],
      'publish': lambda: [setattr(i, 'status', u'published') for i in notices],
    }[action]()
    session.commit()
    return msg.ok('Notices processed: %s' % action)


@admin.route('/buzz/<int:bid>/accept')
@auth.checkroles(['administrator'])
def accept_buzz(bid):
    """Approve messages to appear in the main buzz area"""
    buzz = Buzz.query.get(bid)
    buzz.status = u'approved'
    
    avatar = buzz.owner_avatar or "/static/imgs/avatar.png" 
    query = json.dumps({"type": "moderated", "id": str(bid), "author": str(buzz.owner_nick), "avatar": str(avatar), "content": str(buzz.content), "authortype": str(buzz.type_) }, ensure_ascii=False )
    url = "http://www.gabinetedigital.rs.gov.br/buzz/pub?id="+str(buzz.audience.id)
    f = urllib.urlopen(url, query)
    f.close()
    
    session.commit()
    
    return msg.ok('Buzz accepted')


@admin.route('/buzz/<int:bid>/select')
@auth.checkroles(['administrator'])
def select_buzz(bid):
    """suggest messages to publish"""
    buzz = Buzz.query.get(bid)
    buzz.status = u'selected'
    session.commit()
    return msg.ok('Buzz selected')


@admin.route('/buzz/<int:bid>/delete')
@auth.checkroles(['administrator'])
def delete_buzz(bid):
    """Delete Buzz"""
    buzz = Buzz.query.get(bid)
    if buzz is not None:
        buzz.delete()
        session.commit()
    return msg.ok('Buzz deleted successfuly')


@admin.route('/buzz/<int:bid>/publish')
@auth.checkroles(['administrator'])
def publish_buzz(bid):
    """publish messages"""
    buzz = Buzz.query.get(bid)
    buzz.status = u'published'
    buzz.date_published = datetime.now()
    
    avatar = buzz.owner_avatar or "/static/imgs/avatar.png" 
    query = json.dumps({"type": "published", "id": str(bid), "author": str(buzz.owner_nick), "avatar": str(avatar), "content": str(buzz.content), "authortype": str(buzz.type_) }, ensure_ascii=False )
    url = "http://www.gabinetedigital.rs.gov.br/buzz/pub?id="+str(buzz.audience.id)
    f = urllib.urlopen(url, query)
    f.close()
    
    session.commit()
    return msg.ok('Buzz published')


@admin.route('/buzz/<int:bid>/dont_publish')
@auth.checkroles(['administrator'])
def dont_publish_buzz(bid):
    """not publish messages"""
    buzz = Buzz.query.get(bid)
    buzz.status = u'approved'
    session.commit()
    return msg.ok('Buzz unpublished')
