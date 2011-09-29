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

from flask import Blueprint, render_template, request
from ad.model import Audience, Term, StreamingChannel, session
from .utils import _

admin = Blueprint(
    'admin', __name__,
    template_folder='templates',
    static_folder='static')

@admin.route('/')
def index():
    return 'Please access the /audience url in your browser!'

@admin.route('/audience')
def audiences():
    """Main view, lists all registered audiencces"""
    return render_template('admin/listing.html', title=_(u'Audience'),
                           audience=Audience)

@admin.route('/audience/new', methods=('GET', 'POST'))
def new():
    """Shows the form that creates new audiences and save collected data
    in the database.
    """
    if request.method == 'POST':
        inst = Audience()
        inst.title = request.form['title']
        inst.description = request.form['subject']
        terms = request.form.getlist('term')
        main = request.form['main']
        for term in terms:
            newTerm = Term(hashtag=term, main=(main==term))
            inst.terms.append(newTerm)
        
        inst.owner = 'Admin'
        
        sources = request.form.getlist('source')
        formats = request.form.getlist('format')
        for source, fmt in zip(sources, formats):
            channel = StreamingChannel(source=source, format=fmt)
            inst.sources.append(channel)
        session.commit()
        # msg
        
        return render_template('admin/listing.html', title=_(u'Audience'),audience=Audience)
    
    return render_template('admin/new.html', title=_(u'Audience'))

@admin.route('/audience/<int:aid>', methods=('GET', 'POST'))
def edit(aid):
    """Returns a form to edit an audience and saves new params in the
    database.
    """
    inst = Audience.query.get(aid)
    # An improved search with more params.
    # Audience.query.filter(id=aid, outra_chave=valor)
    if request.method == 'POST':
        inst.title = request.form['title']
        inst.description = request.form['subject']
        
        #delete terms
        instTerm = Term.query.filter_by(audience=inst)
        instTerm.delete()
        terms = request.form.getlist('term')
        main = request.form['main']
        for term in terms:
            newTerm = Term(hashtag=term, main=(main==term))
            inst.terms.append(newTerm)
            
#        terms = request.form.getlist('term')
#        for item in terms:
#            newTerm = Term(hashtag=item)
#            inst.terms.append(newTerm)
#        
        #inst.hashtag = request.form['hashtag']
        inst.owner = 'Admin'

        sources = request.form.getlist('source')
        formats = request.form.getlist('format')
        
        #delete streaming
        inst2 = StreamingChannel.query.filter_by(audience=inst)
        inst2.delete()
        
        for source, fmt in zip(sources, formats):
            channel = StreamingChannel(source=source, format=fmt)
            inst.sources.append(channel)
        session.commit()
        #msg
        return render_template('admin/listing.html', title=_(u'Audience'),audience=Audience)

    return render_template('admin/edit.html', title=_(u'Audience'), inst=inst)

@admin.route('/delete/<int:aid>', methods=['GET', 'POST'])
def remove(aid):
    """Delete audience and streaming in the
    database.
    """
    inst = Audience.query.get(aid)
    inst2 = StreamingChannel.query.filter_by(audience=inst)
    inst3 = Term.query.filter_by(audience=inst)
    
    inst3.delete()
    inst2.delete()
    inst.delete()
    
    session.commit()
    return render_template('admin/listing.html', title=_(u'Audience'),audience=Audience)
