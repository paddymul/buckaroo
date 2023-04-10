// Entry point for the notebook bundle containing custom model definitions.
//
define(function () {
  'use strict';

  window['requirejs'].config({
    map: {
      '*': {
        ipydatagrid: 'nbextensions/ipydatagrid/index',
      },
    },
  });
  // Export the required load_ipython_extension function
  return {
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    load_ipython_extension: function () {},
  };
});
