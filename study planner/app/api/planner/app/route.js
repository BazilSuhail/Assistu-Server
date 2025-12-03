import { NextResponse } from 'next/server';

// Re-using the mock data reference would require a real DB or external store.
// This is just for structure demonstration.
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