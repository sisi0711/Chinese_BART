
var currentQuery = 'The quick brown fox jumped over the lazy dog.';
var currentSentences = '';
var currentText = '';

// ----------------------------------------------------------------------------
// HELPERS
// ----------------------------------------------------------------------------

/**
 * Add the startsWith function to the String class
 */
if (typeof String.prototype.startsWith != 'function') {
  // see below for better implementation!
  String.prototype.startsWith = function (str){
    return this.indexOf(str) === 0;
  };
}

/**
 * A reverse map of PTB tokens to their original gloss
 */
var tokensMap = {
  '-LRB-': '(',
  '-RRB-': ')',
  '-LSB-': '[',
  '-RSB-': ']',
  '-LCB-': '{',
  '-RCB-': '}',
  '``': '"',
  '\'\'': '"',
};

/**
 * A mapping from part of speech tag to the associated
 * visualization color
 */
function posColor(posTag) {
  if (posTag.startsWith('N')) {
    return '#A4BCED';
  } else if (posTag.startsWith('V') || posTag.startsWith('M')) {
    return '#ADF6A2';
  } else if (posTag.startsWith('P')) {
    return '#CCDAF6';
  } else if (posTag.startsWith('I')) {
    return '#FFE8BE';
  } else if (posTag.startsWith('R') || posTag.startsWith('W')) {
    return '#FFFDA8';
  } else if (posTag.startsWith('D') || posTag == 'CD') {
    return '#CCADF6';
  } else if (posTag.startsWith('J')) {
    return '#FFFDA8';
  } else if (posTag.startsWith('T')) {
    return '#FFE8BE';
  } else if (posTag.startsWith('E') || posTag.startsWith('S')) {
    return '#E4CBF6';
  } else if (posTag.startsWith('CC')) {
    return '#FFFFFF';
  } else if (posTag == 'LS' || posTag == 'FW') {
    return '#FFFFFF';
  } else {
    return '#E3E3E3';
  }
}

// ----------------------------------------------------------------------------
// RENDER
// ----------------------------------------------------------------------------

/**
 * Render a given JSON data structure
 */
function render(data) {

  // Error checks
  if (typeof data.sentences === 'undefined') { return; }

  /**
   * Register an entity type (a tag) for Brat
   */
  var entityTypesSet = {};
  var entityTypes = [];

  function addEntityType(name, type, coarseType) {
    if (typeof coarseType === "undefined") {
      coarseType = type;
    }
    // Don't add duplicates
    if (entityTypesSet[type]) return;
    entityTypesSet[type] = true;

	// Get the color of the entity type
    color = '#ffccaa';
    if (name == 'POS') {
      color = posColor(type);
    }

    // Register the type
    entityTypes.push({
      type: type,
      labels : [type],
      bgColor: color,
      borderColor: 'darken'
    });
  }

  /**
   * Register a relation type (an arc) for Brat
   */
  var relationTypesSet = {};
  var relationTypes = [];
  function addRelationType(type, symmetricEdge) {
    // Prevent adding duplicates
    if (relationTypesSet[type]) return;
    relationTypesSet[type] = true;
    // Default arguments
    if (typeof symmetricEdge === 'undefined') { symmetricEdge = false; }
    // Add the type
    relationTypes.push({
      type: type,
      labels: [type],
      dashArray: (symmetricEdge ? '3,3' : undefined),
      arrowHead: (symmetricEdge ? 'none' : undefined),
    });
  }

  //
  // Construct text of annotation
  //
  currentText = [];  // GLOBAL
  currentSentences = data.sentences;  // GLOBAL
  data.sentences.forEach(function(sentence) {
    for (var i = 0; i < sentence.tokens.length; ++i) {
      var token = sentence.tokens[i];
      var word = token.word;
      if (!(typeof tokensMap[word] === "undefined")) {
        word = tokensMap[word];
      }
      if (i > 0) { currentText.push(' '); }
      token.characterOffsetBegin = currentText.length;
      for (var j = 0; j < word.length; ++j) {
        currentText.push(word[j]);
      }
      token.characterOffsetEnd = currentText.length;
    }
    currentText.push('\n');
  });
  currentText = currentText.join('');

  //
  // Shared variables
  // These are what we'll render in BRAT
  //
  // (pos)
  var posEntities = [];

  // (dependencies)
  var depsRelations = [];
  var deps2Relations = [];

  //
  // Loop over sentences.
  // This fills in the variables above.
  //
  for (var sentI = 0; sentI < data.sentences.length; ++sentI) {
    var sentence = data.sentences[sentI];
    var index = sentence.index;
    var tokens = sentence.tokens;
    var deps = sentence['basicDependencies'];

    // POS tags
    /**
     * Generate a POS tagged token id
     */
    function posID(i) {
      return 'POS_' + sentI + '_' + i;
    }
    if (tokens.length > 0 && typeof tokens[0].pos !== 'undefined') {
      for (var i = 0; i < tokens.length; i++) {
        var token = tokens[i];
        var pos = token.pos;
        var begin = parseInt(token.characterOffsetBegin);
        var end = parseInt(token.characterOffsetEnd);
        addEntityType('POS', pos);
        posEntities.push([posID(i), pos, [[begin, end]]]);
      }
    }


    // Dependency parsing
    /**
     * Process a dependency tree from JSON to Brat relations
     */
    function processDeps(name, deps) {
      var relations = [];
      // Format: [${ID}, ${TYPE}, [[${ARGNAME}, ${TARGET}], [${ARGNAME}, ${TARGET}]]]
      for (var i = 0; i < deps.length; i++) {
        var dep = deps[i];
        var governor = dep.governor - 1;
        var dependent = dep.dependent - 1;
        if (governor == -1) continue;
        addRelationType(dep.dep);
        relations.push([name + '_' + sentI + '_' + i, dep.dep, [['governor', posID(governor)], ['dependent', posID(dependent)]]]);
      }
      return relations;
    }
    // Actually add the dependencies
    if (typeof deps !== 'undefined') {
      depsRelations = depsRelations.concat(processDeps('dep', deps));
    }

  }  // End sentence loop

  //
  // Actually render the elements
  //

  /**
   * Helper function to render a given set of entities / relations
   * to a Div, if it exists.
   */
  function embed(container, entities, relations) {
    var text = currentText;
    if ($('#' + container).length > 0) {
      Util.embed(container,
                 {entity_types: entityTypes, relation_types: relationTypes},
                 {text: text, entities: entities, relations: relations}
                );
    }
  }

  // Render each annotation
  head.ready(function() {
    embed('deps', posEntities, depsRelations);
    embed('deps2', posEntities, depsRelations);
  });

}  // End render function



// ----------------------------------------------------------------------------
// MAIN
// ----------------------------------------------------------------------------

/**
 * MAIN()
 *
 * The entry point of the page
 */

      $(document).ready(function(){
        $('#base').hide();
        $('#annotations').hide();
        $('#enhance').hide();
        $('#annotations_un').hide();
        $("#example").change(function(){
          var exa = document.getElementById("example");
          var query = exa.options[exa.selectedIndex].value;
          $.ajax({
                url:'/demo/',
                type:'POST',
                async:false,
                data:JSON.stringify({
                  "query":query,
                }),
                dataType: 'json',
                contentType: 'application/json',
                success: function(result) {
                  var data_all=$.parseJSON(JSON.stringify(result));
                  data=data_all.data1
                  data_un=data_all.data2

                  $('#annotations').empty();
                    function createAnnotationDiv(id, selector, label) {
                      ok = false;
                      if (typeof data[selector] !== 'undefined') {
                        ok = true;
                      } else if (typeof data.sentences !== 'undefined' && data.sentences.length > 0) {
                        if (typeof data.sentences[0][selector] !== 'undefined') {
                          ok = true;
                        } else if (typeof data.sentences[0].tokens != 'undefined' && data.sentences[0].tokens.length > 0) {
                          ok = (typeof data.sentences[0].tokens[0][selector] !== 'undefined');
                        }
                      }
                      if (ok) {
                        $('#annotations').append('<div id="' + id + '"></div>');
                      }
                    } //end of function
                  createAnnotationDiv('deps',     'basicDependencies',                   'Dependencies'      );
                  $('#annotations').show();
                  $('#base').show();
                  // Render
				  render(data);

				  $('#annotations_un').empty();
                    function createAnnotationDiv_un(id, selector, label) {
                      ok = false;
                      if (typeof data_un[selector] !== 'undefined') {
                        ok = true;
                      } else if (typeof data_un.sentences !== 'undefined' && data_un.sentences.length > 0) {
                        if (typeof data_un.sentences[0][selector] !== 'undefined') {
                          ok = true;
                        } else if (typeof data_un.sentences[0].tokens != 'undefined' && data_un.sentences[0].tokens.length > 0) {
                          ok = (typeof data_un.sentences[0].tokens[0][selector] !== 'undefined');
                        }
                      }
                      if (ok) {
                        $('#annotations_un').append('<div id="' + id + '2"></div>');
                      }
                    } //end of function
                  createAnnotationDiv_un('deps',     'basicDependencies',                   'Dependencies'      );
                  $('#search').val(data_un.sentence_get);
                  $('#annotations_un').show();
                  $('#enhance').show();
                  // Render
				  render(data_un);

                }, //end of success
                error: function( XMLResponse ) {   // 这个函数是干吗的？
				  alert( XMLResponse.responseText )
			    }
          }); //end of ajax
          event.preventDefault(); //这句话很重要？
		  event.stopPropagation();
		  return false;
        }); //end of change

        $("#submit_b").click(function(){
          var exa = document.getElementById("search");
          var query = exa.value;
          if (query == ""){
            query = "美存在于愿望的实现之时。"
          }
          $.ajax({
                url:'/demo/',
                type:'POST',
                async:false,
                data:JSON.stringify({
                  "query":query,
                }),
                dataType: 'json',
                contentType: 'application/json',
                success: function(result) {
                  var data_all=$.parseJSON(JSON.stringify(result));
                  data=data_all.data1
                  data_un=data_all.data2

                  $('#annotations').empty();
                    function createAnnotationDiv(id, selector, label) {
                      ok = false;
                      if (typeof data[selector] !== 'undefined') {
                        ok = true;
                      } else if (typeof data.sentences !== 'undefined' && data.sentences.length > 0) {
                        if (typeof data.sentences[0][selector] !== 'undefined') {
                          ok = true;
                        } else if (typeof data.sentences[0].tokens != 'undefined' && data.sentences[0].tokens.length > 0) {
                          ok = (typeof data.sentences[0].tokens[0][selector] !== 'undefined');
                        }
                      }
                      if (ok) {
                        $('#annotations').append('<div id="' + id + '"></div>');
                      }
                    } //end of function
                  createAnnotationDiv('deps',     'basicDependencies',                   'Dependencies'      );
                  $('#annotations').show();
                  $('#base').show();
                  // Render
				  render(data);

				  $('#annotations_un').empty();
                    function createAnnotationDiv_un(id, selector, label) {
                      ok = false;
                      if (typeof data_un[selector] !== 'undefined') {
                        ok = true;
                      } else if (typeof data_un.sentences !== 'undefined' && data_un.sentences.length > 0) {
                        if (typeof data_un.sentences[0][selector] !== 'undefined') {
                          ok = true;
                        } else if (typeof data_un.sentences[0].tokens != 'undefined' && data_un.sentences[0].tokens.length > 0) {
                          ok = (typeof data_un.sentences[0].tokens[0][selector] !== 'undefined');
                        }
                      }
                      if (ok) {
                        $('#annotations_un').append('<div id="' + id + '2"></div>');
                      }
                    } //end of function
                  createAnnotationDiv_un('deps',     'basicDependencies',                   'Dependencies'      );
                  $('#search').val(data_un.sentence_get);
                  $('#annotations_un').show();
                  $('#enhance').show();
                  // Render
				  render(data_un);

                }, //end of success
                error: function( XMLResponse ) {   // 这个函数是干吗的？
				  alert( XMLResponse.responseText )
			    }
          }); //end of ajax
          event.preventDefault(); //这句话很重要？
		  event.stopPropagation();
		  return false;
        }); //end of click
      });