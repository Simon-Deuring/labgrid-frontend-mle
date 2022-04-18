import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PlaceResetDialogComponent } from './place-reset-dialog.component';

describe('PlaceResetDialogComponent', () => {
    let component: PlaceResetDialogComponent;
    let fixture: ComponentFixture<PlaceResetDialogComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [PlaceResetDialogComponent],
        }).compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(PlaceResetDialogComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
