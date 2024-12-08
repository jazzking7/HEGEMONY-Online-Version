$(document).ready(function () {
    $('input[type="number"]').on('input', function () {
        let value = parseInt($(this).val(), 10) || 0;
        value = Math.max(0, Math.min(value, 200));
        $(this).val(value);
    });
    
    $('input[name="simulationMode"]').change(function() {
        if ($(this).val() === 'battleSimulation') {
            $('#description').text('Approximating win rate by simulating 1000 battles using the given stats.');
            $('#attackerTroopSizeContainer, #defenderTroopSizeContainer').removeClass('d-none');
        } else {
            $('#description').text('Approximating win rate by simulating 10,000 rolls using the given stats.');
            $('#attackerTroopSizeContainer, #defenderTroopSizeContainer').addClass('d-none');
        }
    });    

    // Add click function to the Start Simulation button
    $('#startSimulation').click(function () {
        // Get selected simulation mode
        const simulationMode = $('input[name="simulationMode"]:checked').val();

        // Collect attacker stats
        const attackerStats = {
            industrialLevel: parseInt($('#attackerIndustrialLevel').val(), 10) || 6, // Default: 6
            infrastructureLevel: parseInt($('#attackerInfrastructureLevel').val(), 10) || 3, // Default: 3
            minRoll: parseInt($('#attackerMinRoll').val(), 10) || 1, // Default: 1
            damageMultiplier: parseInt($('#attackerDamageMultiplier').val(), 10) || 1, // Default: 1
            nullificationRate: parseInt($('#attackerNullificationRate').val(), 10) || 0 // Default: 0
        };

        // If in battle simulation mode, collect troop size
        if (simulationMode === 'battleSimulation') {
            attackerStats.troopSize = parseInt($('#attackerTroopSize').val(), 10) || 1; // Default: 1
        }

        // Collect defender stats
        const defenderStats = {
            industrialLevel: parseInt($('#defenderIndustrialLevel').val(), 10) || 6, // Default: 6
            infrastructureLevel: parseInt($('#defenderInfrastructureLevel').val(), 10) || 3, // Default: 3
            minRoll: parseInt($('#defenderMinRoll').val(), 10) || 1, // Default: 1
            damageMultiplier: parseInt($('#defenderDamageMultiplier').val(), 10) || 1, // Default: 1
            nullificationRate: parseInt($('#defenderNullificationRate').val(), 10) || 0 // Default: 0
        };

        // If in battle simulation mode, collect troop size
        if (simulationMode === 'battleSimulation') {
            defenderStats.troopSize = parseInt($('#defenderTroopSize').val(), 10) || 1; // Default: 1
        }

        // Emit the simulation data to the backend
        const simulationData = { 
            simulationMode, 
            attackerStats, 
            defenderStats 
        };

        socket.emit('send_simulation_data', simulationData);

        console.log('Simulation data sent:', simulationData);
    });

    // Listen for simulation results from the backend
    socket.on('get_simulation_result', function (data) {
        console.log('Simulation result received:', data);

        // Extract the results
        const {
            attackerWinAll,
            attackerAdvantage,
            split,
            defenderAdvantage,
            defenderWinAll
        } = data;

        // Update the result card with the simulation results
        const resultCard = $('#resultCard');
        const resultBody = resultCard.find('.card-body');

        // Clear existing content
        resultBody.empty();

        // Add result lines
        resultBody.append(`
            <div style="display: flex; justify-content: space-between;">
                <span>Attacker wins all:</span>
                <span>${attackerWinAll}%</span>
            </div>
        `);
        resultBody.append(`
            <div style="display: flex; justify-content: space-between;">
                <span>Attacker advantage:</span>
                <span>${attackerAdvantage}%</span>
            </div>
        `);
        resultBody.append(`
            <div style="display: flex; justify-content: space-between;">
                <span>Split:</span>
                <span>${split}%</span>
            </div>
        `);
        resultBody.append(`
            <div style="display: flex; justify-content: space-between;">
                <span>Defender advantage:</span>
                <span>${defenderAdvantage}%</span>
            </div>
        `);
        resultBody.append(`
            <div style="display: flex; justify-content: space-between;">
                <span>Defender wins all:</span>
                <span>${defenderWinAll}%</span>
            </div>
        `);

        // Show the result card
        resultCard.removeClass('d-none');
    });

    // Listen for battle simulation results from the backend
    socket.on('get_battle_results', function (data) {
        console.log('Battle simulation result received:', data);

        // Extract the results
        const {
            attackerWinRate,
            defenderWinRate,
            avgAttackerDamage,
            avgDefenderDamage,
            avgAttackerDamageOnLoss,
            avgDefenderDamageOnLoss
        } = data;

        // Update the result card with the battle simulation results
        const resultCard = $('#resultCard');
        const resultBody = resultCard.find('.card-body');

        // Clear existing content
        resultBody.empty();

        // Add result lines
        resultBody.append(`
            <div style="display: flex; justify-content: space-between;">
                <span>Attacker win rate:</span>
                <span>${attackerWinRate}%</span>
            </div>
        `);
        resultBody.append(`
            <div style="display: flex; justify-content: space-between;">
                <span>Defender win rate:</span>
                <span>${defenderWinRate}%</span>
            </div>
        `);
        resultBody.append(`
            <div style="display: flex; justify-content: space-between;">
                <span>Average attacker damage:</span>
                <span>${avgAttackerDamage}</span>
            </div>
        `);
        resultBody.append(`
            <div style="display: flex; justify-content: space-between;">
                <span>Average defender damage:</span>
                <span>${avgDefenderDamage}</span>
            </div>
        `);
        resultBody.append(`
            <div style="display: flex; justify-content: space-between;">
                <span>Average attacker damage on loss:</span>
                <span>${avgAttackerDamageOnLoss}</span>
            </div>
        `);
        resultBody.append(`
            <div style="display: flex; justify-content: space-between;">
                <span>Average defender damage on loss:</span>
                <span>${avgDefenderDamageOnLoss}</span>
            </div>
        `);

        // Show the result card
        resultCard.removeClass('d-none');
    });
});