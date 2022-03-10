import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PlaceCreationDialogComponent } from './place-creation-dialog.component';

describe('PlaceCreationDialogComponent', () => {
  let component: PlaceCreationDialogComponent;
  let fixture: ComponentFixture<PlaceCreationDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PlaceCreationDialogComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PlaceCreationDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
