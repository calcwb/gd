/* Copyright (C) 2011  Guilherme Guerra <guerrinha@comum.org>
 * Copyright (C) 2011  Governo do Estado do Rio Grande do Sul
 *
 *   Author: Guilherme Guerra <guilherme-guerran@gg.rs.gov.br>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

function showAggregated(parentId) {
    $('#aggregated-' + parentId).slideToggle();
}

function showEncaminhada(parentId) {
    $('#encaminhada-' + parentId).slideToggle();
}

$(document).ready(function () {
    $('#slideshow .controls').tabs('ul.carousel > li', {
        effect: 'fade',
        rotate: true
    }).slideshow({
        clickable: false
    });

    if ($('#slideshow .controls').length > 0) {
        window.setInterval(function () {
            $("#slideshow .controls").data("tabs").next();
        }, 10000);
    }


});
