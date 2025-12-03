import { NextResponse } from 'next/server';

export async function PUT(request, { params }) {
    const id = params.id;
    const body = await request.json();
    // Logic to update the plan in your database using 'id'
    return NextResponse.json({ message: `Study plan ${id} updated`, data: body });
}

export async function DELETE(request, { params }) {
    const id = params.id;
    // Logic to delete the plan from your database using 'id'
    return NextResponse.json({ message: `Study plan ${id} deleted` });
}

export async function PATCH(request, { params }) {
    const id = params.id;
    const body = await request.json();
    // Logic to partially update the plan in your database using 'id'
    return NextResponse.json({ message: `Study plan ${id} partially updated`, data: body });
}

export async function PATCH(request, { params }) {
    const id = params.id;
    const body = await request.json();
    // Logic to partially update the plan in your database using 'id'
    return NextResponse.json({ message: `Study plan ${id} partially updated`, data: body });
}