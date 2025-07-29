var UseCases = {
  // TFLEX Usecases list starts.....
  105: {
    title: "Symmetric Authentication",
    selected: false,
    ids: ["Slot3"],
  }
};

/* Display the TrustFLEX development boards */
$(document).ready(function () {
  for (var key in UseCases) {
    if (parseInt(key) < 200) {
      $('#hexGrid').append(
        $('<li>', { 'class': 'hex' }).append(
          $('<div>', { 'class': 'hexOut' }).append(
            $('<div>', { 'class': 'hexIn' }).append(
              $('<a>', { 'class': 'hexLink', 'id': key }).append(
                // $('<img>', {'src':UseCases[key].imgpath}),
                $('<p>', { 'text': UseCases[key].title }),
                $('<div>', { 'class': "onclick_usecase" }).append(
                  $('<img>', { 'src': "../images/check-mark-png-11553206004impjy81rdu.png" })
                ))))))
    }
  }
});


$(document).on("click", ".secure_provisioning_guide", function () {
  open_link("Documentation.html#" + $(this).attr('id'));
});

$(document).on("click", ".image_btn", function () {
  $(this).toggleClass('active');
  toggleUseCase($(this).attr('id'));
});

$(document).on("click", ".hexLink", function () {
  $(this).toggleClass('select');
  toggleUseCase($(this).attr('id'));
});

function clearSelectedUseCases(board) {
  for (var ele = 0; ele < Boards[board].usecases.length; ele++) {
    if (UseCases[Boards[board].usecases[ele]].selected === true) {
      toggleUseCase(Boards[board].usecases[ele]);
    }
  }
}

function toggleUseCase(useCase) {
  if (UseCases[useCase].selected === false) {
    UseCases[useCase].ids.forEach(element => {
      var rowElement = document.getElementById(element);
      rowElement.style['backgroundColor'] = 'LightSalmon'
    });
    UseCases[useCase].selected = true;
  } else {
    UseCases[useCase].ids.forEach(element => {
      var rowElement = document.getElementById(element);
      rowElement.style['backgroundColor'] = 'white';
    });
    UseCases[useCase].selected = false;
  }
}

function validateUseCaseSlots() {
  var usecaseElements;
  var alertUseCasesNames = "";
  var alertUseCaseSlots = "";
  var alertStatus = false;
  var radioName;

  for (usecaseElements in UseCases) {
    if (UseCases[usecaseElements].selected == true) {
      for (let i = 0; i < UseCases[usecaseElements].ids.length; i++) {
        var element = UseCases[usecaseElements].ids[i];
        radioName = element.toLowerCase() + "dataopt";
        if (getFormRadioValue(formNameMain, radioName) == "unused") {
          if (!alertUseCaseSlots.includes(element)) {
            alertUseCaseSlots += element + "\r\n";
            alertStatus = true;
          }
        }
      }
    }
  }

  if (alertStatus) {
    alert("For the usecases selected, Data is required in the following slots: \r\n" + alertUseCaseSlots);
  }
  return alertStatus;
}
