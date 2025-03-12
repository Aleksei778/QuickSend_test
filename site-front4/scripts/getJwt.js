export async function getJWTToken() {
    const response = await fetch('/api/v1/get_jwt');
    const data = await response.json();
    console.log(data);
    return data.access_token;
}