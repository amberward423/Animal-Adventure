let game_id = null
let animal_id = null




async function start_game() {
    const response = await fetch('http://127.0.0.1:3000/animal_adventure/start_game')
    const data = await response.json();

    //save game_id
    game_id = data['game_id']
    animal_id = data['animal_id']

    // Get the stats object
    let stats = data['stats'][0];
    console.log(data['airports'])
    update_stats(stats)
    update_airports(data['airports'])

}


function update_stats(stats) {


    stats.animal_id = animal_id;
    document.getElementById('stats').innerText = `
        Money: ${stats.money}
        Range: ${stats.player_range}
        Turn_Time: ${stats.turn_time}
        Location: ${stats.location}
        Animal:  ${stats.animal_id}
        
    `;

}



function update_airports(airports) {
    airports_div = document.getElementById('airports')

    airports_div.innerHTML = '';
    const ul = document.createElement('ul');

    airports.forEach(airport => {
        const li = document.createElement('li');
        li.innerHTML = `
            <strong>${airport.icao}</strong>: ${airport.name}
        `;
        ul.appendChild(li);
    });
    airports_div.appendChild(ul);

    }


async function buy_fuel() {
    const response = await fetch("http://127.0.0.1:3000/animal_adventure/buy_fuel/" + game_id)
    const data = await response.json();
    let stats = data[0]
    if (stats.money < 0){
        document.getElementById("response").textContent = "You don't have money to buy fuel "
        return;

    }
    update_stats(stats)


}
async function update_location() {
    console.log('Changing airport')
    let icao = document.getElementById('icao').value
    const response = await fetch('http://127.0.0.1:3000/animal_adventure/choose_airport/'+game_id+'/'+ icao)
    const data = await response.json();
    let stats = data[0]
    console.log(stats)
    update_stats(stats)
}

async function check_animal()  {
    console.log("checking for animals")
    let current_airport = stats.icao;
    const response = await fetch('http://127.0.0.1:3000/animal_adventure/check_animal/' +game_id+ '/' + current_airport + animal_id)
    const data = await response.json();
    console.log(data)
    update_stats(data)
}

check_animal()


document.getElementById("start").addEventListener("click", start_game);
document.getElementById("buy_fuel").addEventListener("click", buy_fuel);
document.getElementById("update_location").addEventListener("click", update_location);

const name = prompt("write your name :))")

 alert(`${name} a zookeeper from Happy Animals Zoo, and your endangered animals have been taken by a villainous mob boss named Matti, who has taken the animals to the airport to sell and distribute them to new and prospective owners all in very short time. 
` +
     "     But while boarding Matti's private jet, the animals escaped their pens and have now been taken to random airports. \n" +
     "     Matti also dropped his list of private airports where his jet frequently stops to refuel. \n" +
     "     You have pursued and followed Matti to the airport and saw this happening from afar; \n" +
     "     however, after Matti's jet has taken off, you step on a piece of paper which, upon closer inspection, is revealed to be Matti's private airport list. \n" +
     "     Armed with this list and some money, you start off on your animal adventure, where you will rescue and reclaim the endangered animals from your zoo. \n" +
     "     Your task is to first select an airport where you will start. Along this journey, you will need luck, grit, and sisu to help find the animals.Good luck!\"\"\"\n")