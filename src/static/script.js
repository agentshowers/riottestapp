$(document)
    .ajaxStart(function () {
        $("#loadingDiv").css("display","");
    })
    .ajaxStop(function () {
        $("#loadingDiv").css("display","none");
    });

function getMatchData () {
    var summoner = $("#summonerName").val();
    var region = $("#region").val();

    if (summoner == "") {
        $("#summonerName").css("boxShadow", "0 0 8px #CC0000");
        return;
    } 

    $("#summonerName").css("boxShadow", "0 0 0");
    getData(summoner, region)
}

function getData(s, r) {
    $.ajax({
        url: "gamedata",
        data: {
            summoner: s,
            region: r
        },
        success: function(data) {
            displayResult(data)      
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            displayError(XMLHttpRequest)
        }
    });
}

function displayResult(data) {
    var tableHtml = headerRow();
    for (var i = 0; i < data.participants.length; i++) { 
        tableHtml += createRow(data.participants[i]);
    }
    $("#participantTable").html(tableHtml);
    $("#errorMessage").html("");
    $("#gamedata").css("display","");
}

function headerRow () {
    return "<tr><th>Summoner ID</th><th>Summoner Name</th> <th>Team ID</th><th>Champion ID</th><th>Champion Name</th><th>Champion Mastery</th></tr>";
}

function createRow(participant) {
    var tr = "<tr>";
    tr += "<td>" + participant["summonerId"]  + "</td>";
    tr += "<td>" + participant["summonerName"]  + "</td>";
    tr += "<td>" + participant["teamId"]  + "</td>";
    tr += "<td>" + participant["championId"]  + "</td>";
    tr += "<td>" + participant["championName"]  + "</td>";
    tr += "<td><img class='mastery' src='static/images/Mastery_" + participant["championMastery"] + ".png'></td>";
    tr +="</tr>";
    return tr;
}

function displayError(response){
    $("#errorMessage").html("An error occured: " + response.responseText + "<br/> Status Code: " + response.status);
    $("#gamedata").css("display","none");
}