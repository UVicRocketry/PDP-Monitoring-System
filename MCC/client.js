import net from 'net';
import readline from 'readline'

const HOST = '127.0.0.1';
const PORT = 8001;

const client = new net.Socket();

// temp for user input
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
})

client.connect(PORT, HOST, () => {
    console.log('Connected to server');
});

rl.on('line', (input) => {
    client.write(input);
});

client.on('data', (data) => {
    console.log("data:", data.toString());
});

client.on('close', () => {
    console.log("closed");
})