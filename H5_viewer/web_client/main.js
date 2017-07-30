import { wrap } from 'girder/utilities/PluginUtils';
import ItemView from 'girder/views/body/ItemView';

wrap(ItemView, 'render', function (render) {
  this.once('g:rendered', function() {
    this.$('.g-item-header').after('<div class = "g-H5-view"></div>');
    
  }
}
