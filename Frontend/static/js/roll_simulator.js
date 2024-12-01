$(document).ready(function () {
    // Add click function to the Start Simulation button
    $('#startSimulation').click(function () {
        // Collect attacker stats
        const attackerStats = {
            industrialLevel: parseInt($('#attackerIndustrialLevel').val(), 10) || 6, // Default: 6
            infrastructureLevel: parseInt($('#attackerInfrastructureLevel').val(), 10) || 3, // Default: 3
            minRoll: parseInt($('#attackerMinRoll').val(), 10) || 1, // Default: 1
            damageMultiplier: parseInt($('#attackerDamageMultiplier').val(), 10) || 1, // Default: 1
            nullificationRate: parseInt($('#attackerNullificationRate').val(), 10) || 0 // Default: 0
        };

        // Collect defender stats
        const defenderStats = {
            industrialLevel: parseInt($('#defenderIndustrialLevel').val(), 10) || 6, // Default: 6
            infrastructureLevel: parseInt($('#defenderInfrastructureLevel').val(), 10) || 3, // Default: 3
            minRoll: parseInt($('#defenderMinRoll').val(), 10) || 1, // Default: 1
            damageMultiplier: parseInt($('#defenderDamageMultiplier').val(), 10) || 1, // Default: 1
            nullificationRate: parseInt($('#defenderNullificationRate').val(), 10) || 0 // Default: 0
        };

        // Emit the simulation data to the backend
        const simulationData = { attackerStats, defenderStats };
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
});
