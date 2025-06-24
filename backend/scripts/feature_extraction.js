const axios = require('axios');

async function getTransactionDetails(txId) {
    try {
        const response = await axios.get(`https://api.blockcypher.com/v1/btc/main/txs/${txId}`);
        const tx = response.data;
        
        console.log('\n=== Transaktions-Details ===');
        console.log(`Transaktions-ID: ${tx.hash}`);
        console.log(`Block-Höhe: ${tx.block_height}`);
        console.log(`Block-Zeit: ${new Date(tx.block_time * 1000).toLocaleString()}`);
        console.log(`Gebühren: ${tx.fees / 100000000} BTC`);
        console.log(`Größe: ${tx.size} Bytes`);
        console.log(`Bestätigungen: ${tx.confirmations}`);
        
        console.log('\n=== Inputs (Von) ===');
        tx.inputs.forEach((input, index) => {
            console.log(`\nInput #${index + 1}:`);
            console.log(`Adresse: ${input.addresses[0]}`);
            console.log(`Betrag: ${input.output_value / 100000000} BTC`);
            console.log(`Script: ${input.script}`);
        });
        
        console.log('\n=== Outputs (Nach) ===');
        tx.outputs.forEach((output, index) => {
            console.log(`\nOutput #${index + 1}:`);
            console.log(`Adresse: ${output.addresses[0]}`);
            console.log(`Betrag: ${output.value / 100000000} BTC`);
            console.log(`Script: ${output.script}`);
            console.log(`Spent: ${output.spent_by ? 'Ja' : 'Nein'}`);
        });
    } catch (error) {
        console.error('Error:', error.message);
    }
}

// Beispielaufruf mit einer realen Transaktions-ID
// getTransactionDetails('2a7328443c5d607d17d7814e3eb906bb91a93a9071795ac7b760f9e18d6248dc');

async function getAddressMetrics(address) {
    try {
        console.log('Hole Daten für Adresse:', address);
        // Hole alle Transaktionen für die Adresse
        const response = await axios.get(`https://api.blockcypher.com/v1/btc/main/addrs/${address}`);
        const data = response.data;
        
        console.log('API Antwort:', {
            final_balance: data.final_balance,
            total_received: data.total_received,
            total_sent: data.total_sent,
            n_tx: data.n_tx,
            address: data.address,
            hash160: data.hash160
        });

        // Hole die Transaktionen mit Pagination
        console.log('Hole Transaktionsdetails...');
        let allTransactions = [];
        let hasMore = true;
        let before = undefined;
        let retryCount = 0;
        const maxRetries = 5;
        const baseDelay = 2000;

        while (hasMore) {
            try {
                const url = `https://api.blockcypher.com/v1/btc/main/addrs/${address}/full`;
                const params = {
                    limit: 200,
                    before: before,
                    after: undefined,
                    txlimit: 200
                };

                console.log('Hole Transaktionen mit Parametern:', params);
                const txsResponse = await axios.get(url, { params });
                const txsData = txsResponse.data;
                
                console.log('Erhaltene Transaktionen:', txsData.txs ? txsData.txs.length : 0);
                console.log('API Response:', {
                    n_tx: txsData.n_tx,
                    total_received: txsData.total_received,
                    total_sent: txsData.total_sent,
                    final_balance: txsData.final_balance,
                    hasMore: txsData.hasMore
                });

                if (txsData.txs && txsData.txs.length > 0) {
                    // Log transaction details for debugging
                    txsData.txs.forEach((tx, index) => {
                        console.log(`\nTransaktion ${index + 1}:`, {
                            hash: tx.hash,
                            block_height: tx.block_height,
                            block_time: tx.block_time,
                            inputs: tx.inputs.length,
                            outputs: tx.outputs.length
                        });
                    });

                    allTransactions = allTransactions.concat(txsData.txs);
                    const lastTx = txsData.txs[txsData.txs.length - 1];
                    before = lastTx.block_height;
                    console.log('Nächste Seite ab Block:', before);
                    
                    // Überprüfe, ob wir alle Transaktionen haben
                    hasMore = allTransactions.length < data.n_tx;
                    console.log('Noch mehr Transaktionen?', hasMore, 'Gefunden:', allTransactions.length, 'Von:', data.n_tx);
                } else {
                    hasMore = false;
                }

                retryCount = 0;
                const delay = baseDelay + (allTransactions.length * 100);
                console.log(`Warte ${delay/1000} Sekunden vor der nächsten Anfrage...`);
                await new Promise(resolve => setTimeout(resolve, delay));

            } catch (error) {
                if (error.response && error.response.status === 429) {
                    retryCount++;
                    if (retryCount > maxRetries) {
                        console.log('Maximale Anzahl an Wiederholungsversuchen erreicht. Beende Abfrage.');
                        break;
                    }
                    
                    const backoffDelay = baseDelay * Math.pow(2, retryCount);
                    console.log(`Rate limit erreicht. Warte ${backoffDelay/1000} Sekunden vor dem nächsten Versuch...`);
                    await new Promise(resolve => setTimeout(resolve, backoffDelay));
                    continue;
                }
                throw error;
            }
        }

        console.log('Gesamt gefundene Transaktionen:', allTransactions.length);
        console.log('Erwartete Transaktionen:', data.n_tx);
        
        // If we have a balance but no valid transactions, use the balance as a basis
        if (allTransactions.length === 0 || !allTransactions.some(tx => tx.block_time)) {
            if (data.final_balance > 0) {
                console.log('Verwende Kontostand als Basis für Metriken');
                return {
                    totalInputAmount: data.total_received / 100000000,
                    totalOutputAmount: data.total_sent / 100000000,
                    inputOutputDifference: (data.total_received - data.total_sent) / 100000000,
                    inDegree: data.n_tx,
                    outDegree: data.n_tx,
                    lifetimeDays: 0,
                    outputToOutDegreeRatio: data.total_sent / (data.n_tx * 100000000),
                    averageDailyDegrees: { in: data.n_tx, out: data.n_tx },
                    outputChangeStdDev: 0
                };
            }
            throw new Error('Keine gültigen Transaktionen gefunden');
        }
        
        // Filter out transactions without block_time
        const validTransactions = allTransactions.filter(tx => tx.block_time);
        
        // Rest of the metrics calculation remains the same
        let totalInputAmount = 0;
        let totalOutputAmount = 0;
        let inDegree = 0;
        let outDegree = 0;
        let firstTxTime = null;
        let lastTxTime = null;
        let dailyDegrees = {};
        
        validTransactions.forEach(tx => {
            const txTime = new Date(tx.block_time * 1000);
            const txDate = txTime.toISOString().split('T')[0];
            
            if (!firstTxTime || txTime < firstTxTime) firstTxTime = txTime;
            if (!lastTxTime || txTime > lastTxTime) lastTxTime = txTime;
            
            if (!dailyDegrees[txDate]) {
                dailyDegrees[txDate] = { in: 0, out: 0 };
            }
            
            tx.inputs.forEach(input => {
                if (input.addresses && input.addresses.includes(address)) {
                    totalInputAmount += input.output_value || 0;
                    inDegree++;
                    dailyDegrees[txDate].in++;
                }
            });
            
            tx.outputs.forEach(output => {
                if (output.addresses && output.addresses.includes(address)) {
                    totalOutputAmount += output.value || 0;
                    outDegree++;
                    dailyDegrees[txDate].out++;
                }
            });
        });
        
        // Calculate metrics
        const metrics = {
            totalInputAmount: totalInputAmount / 100000000,
            totalOutputAmount: totalOutputAmount / 100000000,
            inputOutputDifference: (totalInputAmount - totalOutputAmount) / 100000000,
            inDegree,
            outDegree,
            lifetimeDays: (lastTxTime - firstTxTime) / (1000 * 60 * 60 * 24),
            outputToOutDegreeRatio: outDegree > 0 ? totalOutputAmount / (outDegree * 100000000) : 0,
            averageDailyDegrees: Object.values(dailyDegrees).reduce((acc, day) => ({
                in: acc.in + day.in,
                out: acc.out + day.out
            }), { in: 0, out: 0 })
        };
        
        // Calculate output change standard deviation
        let outputChanges = [];
        let lastOutput = 0;
        validTransactions.forEach(tx => {
            const currentOutput = tx.outputs
                .filter(output => output.addresses && output.addresses.includes(address))
                .reduce((sum, output) => sum + (output.value || 0), 0);
            
            if (lastOutput > 0) {
                outputChanges.push(currentOutput - lastOutput);
            }
            lastOutput = currentOutput;
        });
        
        if (outputChanges.length > 0) {
            const mean = outputChanges.reduce((a, b) => a + b, 0) / outputChanges.length;
            const variance = outputChanges.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / outputChanges.length;
            metrics.outputChangeStdDev = Math.sqrt(variance) / 100000000;
        } else {
            metrics.outputChangeStdDev = 0;
        }
        
        return metrics;
    } catch (error) {
        console.error('Error:', error.message);
        if (error.response) {
            console.error('API Error:', {
                status: error.response.status,
                data: error.response.data
            });
        }
        return null;
    }
}

// Beispielaufruf
getAddressMetrics('bc1qfheacg600a5kchg74z0nu5pf7xgdehp0ywusakpscjq9u3tl93cqdq6ghg').then(metrics => {
    if (metrics) {
        console.log('\n=== Adress-Metriken ===');
        console.log(`Gesamter Input-Betrag: ${metrics.totalInputAmount} BTC`);
        console.log(`Gesamter Output-Betrag: ${metrics.totalOutputAmount} BTC`);
        console.log(`Differenz Input-Output: ${metrics.inputOutputDifference} BTC`);
        console.log(`In-Degree: ${metrics.inDegree}`);
        console.log(`Out-Degree: ${metrics.outDegree}`);
        console.log(`Lebensdauer: ${metrics.lifetimeDays.toFixed(2)} Tage`);
        console.log(`Output/Out-Degree Verhältnis: ${metrics.outputToOutDegreeRatio}`);
        console.log(`Durchschnittliche tägliche Degrees: In=${metrics.averageDailyDegrees.in}, Out=${metrics.averageDailyDegrees.out}`);
        console.log(`Standardabweichung der Output-Änderungen: ${metrics.outputChangeStdDev} BTC`);
    }
});